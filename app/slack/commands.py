"""
Slack command handlers for the Content Pipeline.
"""

import asyncio
import io
from typing import Dict, Any

from loguru import logger
from slack_sdk.errors import SlackApiError

from app.keyword.processor import KeywordProcessor
from app.keyword.grouper import KeywordGrouper
from app.outline.generator import OutlineGenerator
from app.post_ideas.idea_generator import PostIdeaGenerator
from app.reports.pdf_generator import PDFGenerator
from app.reports.emailer import EmailSender
from app.storage.database import DatabaseManager
from app.storage.cache import CacheManager
from app.slack.formatter import MessageFormatter


class CommandHandler:
    """Handles all Slack command interactions."""
    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db = db_manager
        self.cache = cache_manager
        self.formatter = MessageFormatter()
        
        # Initialize processors
        self.keyword_processor = KeywordProcessor()
        self.keyword_grouper = KeywordGrouper()
        self.outline_generator = OutlineGenerator()
        self.idea_generator = PostIdeaGenerator()
        self.pdf_generator = PDFGenerator()
        self.email_sender = EmailSender()
    
    async def handle_keywords_command(self, command: Dict[str, Any], client):
        """Handle /keywords command."""
        try:
            user_id = command["user_id"]
            channel_id = command["channel_id"]
            text = command.get("text", "").strip()
            
            # Rate limiting check
            if not await self._check_rate_limit(user_id):
                await self._send_rate_limit_message(client, channel_id)
                return
            
            if not text or text == "upload":
                # Show upload instructions
                message = self.formatter.format_upload_instructions()
                await client.chat_postMessage(channel=channel_id, **message)
                
            elif text == "paste":
                # Show paste instructions
                message = self.formatter.format_paste_instructions()
                await client.chat_postMessage(channel=channel_id, **message)
                
            else:
                # Process pasted keywords
                await self._process_keywords_from_text(text, user_id, channel_id, client)
                
        except Exception as e:
            logger.error(f"Error in keywords command: {e}")
            await self._send_error_message(client, command["channel_id"])
    
    async def handle_process_command(self, command: Dict[str, Any], client):
        """Handle /process command."""
        try:
            user_id = command["user_id"]
            channel_id = command["channel_id"]
            batch_id = command.get("text", "").strip()
            
            if not batch_id:
                message = self.formatter.format_process_usage()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Check if batch exists and belongs to user
            batch = await self.db.get_keyword_batch(batch_id)
            if not batch:
                message = self.formatter.format_batch_not_found()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            if batch["user_id"] != user_id:
                message = self.formatter.format_unauthorized_batch()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Start processing
            await self._start_batch_processing(batch, channel_id, client)
            
        except Exception as e:
            logger.error(f"Error in process command: {e}")
            await self._send_error_message(client, command["channel_id"])
    
    async def handle_history_command(self, command: Dict[str, Any], client):
        """Handle /history command."""
        try:
            user_id = command["user_id"]
            channel_id = command["channel_id"]
            
            # Get user's processing history
            history = await self.db.get_user_history(user_id, limit=5)
            
            if not history:
                message = self.formatter.format_no_history()
            else:
                message = self.formatter.format_history(history)
            
            await client.chat_postMessage(channel=channel_id, **message)
            
        except Exception as e:
            logger.error(f"Error in history command: {e}")
            await self._send_error_message(client, command["channel_id"])
    
    async def handle_regenerate_command(self, command: Dict[str, Any], client):
        """Handle /regenerate command."""
        try:
            user_id = command["user_id"]
            channel_id = command["channel_id"]
            batch_id = command.get("text", "").strip()
            
            if not batch_id:
                message = self.formatter.format_regenerate_usage()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Check batch ownership
            batch = await self.db.get_keyword_batch(batch_id)
            if not batch or batch["user_id"] != user_id:
                message = self.formatter.format_batch_not_found()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Start regeneration
            await self._regenerate_outlines(batch, channel_id, client)
            
        except Exception as e:
            logger.error(f"Error in regenerate command: {e}")
            await self._send_error_message(client, command["channel_id"])
    
    async def handle_file_upload(self, event: Dict[str, Any], client):
        """Handle file upload events."""
        try:
            file_info = event["file"]
            user_id = event["user_id"]
            channel_id = event.get("channel_id")
            
            # Check if it's a CSV file
            if not file_info["name"].endswith(".csv"):
                return  # Ignore non-CSV files
            
            # Download and process the file
            file_content = await self._download_slack_file(client, file_info)
            if file_content:
                await self._process_keywords_from_csv(file_content, user_id, channel_id, client)
                
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
    
    async def handle_message_keywords(self, event: Dict[str, Any], client):
        """Handle messages that might contain keywords."""
        try:
            text = event.get("text", "")
            user_id = event["user"]
            channel_id = event["channel"]
            
            # Simple keyword detection
            if self._looks_like_keywords(text):
                # Ask if user wants to process these as keywords
                message = self.formatter.format_keyword_detection(text[:100])
                await client.chat_postMessage(channel=channel_id, **message)
                
        except Exception as e:
            logger.error(f"Error handling message keywords: {e}")
    
    async def handle_app_mention(self, event: Dict[str, Any], client):
        """Handle app mentions."""
        try:
            text = event.get("text", "")
            channel_id = event["channel"]
            
            # Provide help information
            message = self.formatter.format_help_message()
            await client.chat_postMessage(channel=channel_id, **message)
            
        except Exception as e:
            logger.error(f"Error handling app mention: {e}")
    
    async def _process_keywords_from_text(self, text: str, user_id: str, channel_id: str, client):
        """Process keywords from pasted text."""
        try:
            # Parse and clean keywords
            keywords = self.keyword_processor.parse_keywords(text)
            
            if not keywords:
                message = self.formatter.format_no_keywords_found()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Create batch in database
            batch = await self.db.create_keyword_batch({
                "user_id": user_id,
                "keywords": keywords,
                "keyword_count": len(keywords),
                "status": "uploaded",
                "source": "text"
            })
            
            # Send confirmation
            message = self.formatter.format_keywords_uploaded(batch["id"], len(keywords))
            await client.chat_postMessage(channel=channel_id, **message)
            
            logger.info(f"Keywords uploaded: batch {batch['id']}, {len(keywords)} keywords")
            
        except Exception as e:
            logger.error(f"Error processing keywords from text: {e}")
            await self._send_error_message(client, channel_id)
    
    async def _process_keywords_from_csv(self, csv_content: str, user_id: str, channel_id: str, client):
        """Process keywords from CSV content."""
        try:
            # Parse CSV
            keywords = await self.keyword_processor.parse_csv(csv_content)
            
            if not keywords:
                message = self.formatter.format_no_keywords_found()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Create batch
            batch = await self.db.create_keyword_batch({
                "user_id": user_id,
                "keywords": keywords,
                "keyword_count": len(keywords),
                "status": "uploaded",
                "source": "csv"
            })
            
            # Send confirmation
            message = self.formatter.format_keywords_uploaded(batch["id"], len(keywords))
            await client.chat_postMessage(channel=channel_id, **message)
            
            logger.info(f"CSV processed: batch {batch['id']}, {len(keywords)} keywords")
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            await self._send_error_message(client, channel_id)
    
    async def _start_batch_processing(self, batch: Dict[str, Any], channel_id: str, client):
        """Start processing a keyword batch."""
        try:
            batch_id = batch["id"]
            
            # Check for processing lock
            lock_key = f"processing:{batch_id}"
            if await self.cache.exists(lock_key):
                message = self.formatter.format_already_processing()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Set processing lock
            await self.cache.set(lock_key, "processing", ttl=1800)  # 30 minutes
            
            # Send start message
            message = self.formatter.format_processing_started(batch_id, batch["keyword_count"])
            await client.chat_postMessage(channel=channel_id, **message)
            
            # Start background processing
            asyncio.create_task(self._process_batch_background(batch, channel_id, client))
            
        except Exception as e:
            logger.error(f"Error starting batch processing: {e}")
            await self._send_error_message(client, channel_id)
    
    async def _process_batch_background(self, batch: Dict[str, Any], channel_id: str, client):
        """Process batch in the background."""
        batch_id = batch["id"]
        
        try:
            # Update status
            await self.db.update_keyword_batch(batch_id, {"status": "processing"})
            
            # Step 1: Group keywords
            await client.chat_postMessage(
                channel=channel_id,
                **self.formatter.format_processing_step("Grouping keywords", 1, 4)
            )
            
            groups = await self.keyword_grouper.group_keywords(batch["keywords"])
            
            # Save groups to database
            for group in groups:
                await self.db.create_keyword_group({
                    "batch_id": batch_id,
                    "keywords": group["keywords"],
                    "cluster_name": group["name"],
                    "similarity_score": group.get("score", 0.0)
                })
            
            # Step 2: Generate outlines
            await client.chat_postMessage(
                channel=channel_id,
                **self.formatter.format_processing_step("Generating outlines", 2, 4)
            )
            
            for group in groups:
                outline = await self.outline_generator.generate_outline(group["keywords"])
                await self.db.create_outline({
                    "group_id": group["id"],
                    "outline_data": outline
                })
            
            # Step 3: Generate post ideas
            await client.chat_postMessage(
                channel=channel_id,
                **self.formatter.format_processing_step("Generating post ideas", 3, 4)
            )
            
            post_ideas = await self.idea_generator.generate_ideas(groups)
            
            # Step 4: Generate report
            await client.chat_postMessage(
                channel=channel_id,
                **self.formatter.format_processing_step("Generating report", 4, 4)
            )
            
            report = await self.pdf_generator.generate_report(batch_id, groups, post_ideas)
            
            # Update batch status
            await self.db.update_keyword_batch(batch_id, {
                "status": "completed",
                "completed_at": "now()"
            })
            
            # Send completion message
            message = self.formatter.format_processing_completed(
                batch_id, len(groups), len(post_ideas), report["download_url"]
            )
            await client.chat_postMessage(channel=channel_id, **message)
            
            # Send email if configured
            if report.get("email_sent"):
                await client.chat_postMessage(
                    channel=channel_id,
                    **self.formatter.format_email_sent()
                )
            
            # Release lock
            await self.cache.delete(f"processing:{batch_id}")
            
            logger.info(f"Batch {batch_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {e}")
            
            # Update status and release lock
            await self.db.update_keyword_batch(batch_id, {"status": "failed"})
            await self.cache.delete(f"processing:{batch_id}")
            
            # Send error message
            await client.chat_postMessage(
                channel=channel_id,
                **self.formatter.format_processing_failed(batch_id)
            )
    
    async def _regenerate_outlines(self, batch: Dict[str, Any], channel_id: str, client):
        """Regenerate outlines for a batch."""
        try:
            batch_id = batch["id"]
            
            # Get existing groups
            groups = await self.db.get_keyword_groups_by_batch(batch_id)
            
            if not groups:
                message = self.formatter.format_no_groups_found()
                await client.chat_postMessage(channel=channel_id, **message)
                return
            
            # Send start message
            message = self.formatter.format_regeneration_started(batch_id)
            await client.chat_postMessage(channel=channel_id, **message)
            
            # Regenerate outlines
            for group in groups:
                outline = await self.outline_generator.generate_outline(group["keywords"])
                await self.db.update_outline(group["id"], {"outline_data": outline})
            
            # Send completion message
            message = self.formatter.format_regeneration_completed(batch_id)
            await client.chat_postMessage(channel=channel_id, **message)
            
        except Exception as e:
            logger.error(f"Error regenerating outlines: {e}")
            await self._send_error_message(client, channel_id)
    
    async def _download_slack_file(self, client, file_info: Dict[str, Any]) -> str:
        """Download a file from Slack."""
        try:
            # Get file content
            response = await client.files_info(file=file_info["id"])
            file_url = response["file"]["url_private"]
            
            # Download file content
            file_response = await client.api_call(
                "files.info",
                http_verb="GET",
                file=file_info["id"]
            )
            
            # Return file content as string
            return file_response.get("content", "")
            
        except Exception as e:
            logger.error(f"Error downloading Slack file: {e}")
            return ""
    
    def _looks_like_keywords(self, text: str) -> bool:
        """Check if text looks like a keyword list."""
        if not text or len(text) < 20:
            return False
        
        # Check for keyword indicators
        comma_count = text.count(",")
        newline_count = text.count("\n")
        
        return (comma_count > 2 and len(text.split(",")) > 3) or \
               (newline_count > 2 and len(text.split("\n")) > 3)
    
    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits."""
        key = f"rate_limit:{user_id}"
        current = await self.cache.get(key)
        
        if current is None:
            await self.cache.set(key, 1, ttl=900)  # 15 minutes
            return True
        
        if current >= 10:  # Max 10 requests per 15 minutes
            return False
        
        await self.cache.increment(key)
        return True
    
    async def _send_rate_limit_message(self, client, channel_id: str):
        """Send rate limit exceeded message."""
        message = self.formatter.format_rate_limit_exceeded()
        await client.chat_postMessage(channel=channel_id, **message)
    
    async def _send_error_message(self, client, channel_id: str):
        """Send generic error message."""
        message = self.formatter.format_error_message()
        await client.chat_postMessage(channel=channel_id, **message)
