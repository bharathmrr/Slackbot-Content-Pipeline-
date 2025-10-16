"""
Flask-based Slack bot implementation with interactive components.
"""

import asyncio
import json
from typing import Dict, Any
from slack_bolt import App, Say, Ack
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from loguru import logger

from app.config import get_settings
from app.slack.commands import CommandHandler
from app.slack.formatter import MessageFormatter
from app.storage.database import DatabaseManager
from app.storage.cache import CacheManager


class FlaskSlackBot:
    """Flask-based Slack bot with interactive components."""
    
    def __init__(self, slack_app: App, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.app = slack_app
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.settings = get_settings()
        
        # Initialize components
        self.command_handler = CommandHandler(db_manager, cache_manager)
        self.formatter = MessageFormatter()
    
    def register_handlers(self):
        """Register all Slack event handlers."""
        
        # Slash Commands
        @self.app.command("/keywords")
        def handle_keywords_command(ack: Ack, command: dict, say: Say):
            ack()
            self._handle_keywords_command(command, say)
        
        @self.app.command("/process")
        def handle_process_command(ack: Ack, command: dict, say: Say):
            ack()
            self._handle_process_command(command, say)
        
        @self.app.command("/history")
        def handle_history_command(ack: Ack, command: dict, say: Say):
            ack()
            self._handle_history_command(command, say)
        
        @self.app.command("/regenerate")
        def handle_regenerate_command(ack: Ack, command: dict, say: Say):
            ack()
            self._handle_regenerate_command(command, say)
        
        # Interactive Components
        @self.app.action("start_processing")
        def handle_start_processing(ack: Ack, body: dict, say: Say):
            ack()
            self._handle_start_processing_button(body, say)
        
        @self.app.action("process_keywords")
        def handle_process_keywords(ack: Ack, body: dict, say: Say):
            ack()
            self._handle_process_keywords_button(body, say)
        
        @self.app.action("ignore_keywords")
        def handle_ignore_keywords(ack: Ack, body: dict):
            ack()
            self._handle_ignore_keywords_button(body)
        
        @self.app.action("download_report")
        def handle_download_report(ack: Ack, body: dict):
            ack()
            # No additional action needed for URL buttons
        
        # File Upload Events
        @self.app.event("file_shared")
        def handle_file_shared(event: dict, say: Say):
            self._handle_file_upload(event, say)
        
        # Message Events
        @self.app.event("message")
        def handle_message(event: dict, say: Say):
            # Only process messages that might contain keywords
            if self._might_contain_keywords(event.get("text", "")):
                self._handle_message_keywords(event, say)
        
        # App Mention Events
        @self.app.event("app_mention")
        def handle_app_mention(event: dict, say: Say):
            self._handle_app_mention(event, say)
        
        # Error Handler
        @self.app.error
        def handle_errors(error: Exception, body: dict):
            logger.error(f"Slack error: {error}")
            logger.debug(f"Error body: {body}")
            return BoltResponse(status=200, body="")
    
    def _handle_keywords_command(self, command: dict, say: Say):
        """Handle /keywords command."""
        try:
            text = command.get("text", "").strip()
            user_id = command["user_id"]
            
            if not text or text == "upload":
                message = self.formatter.format_upload_instructions()
                say(**message)
                
            elif text == "paste":
                message = self.formatter.format_paste_instructions()
                say(**message)
                
            else:
                # Process pasted keywords
                self._process_keywords_from_text(text, user_id, say)
                
        except Exception as e:
            logger.error(f"Error in keywords command: {e}")
            self._send_error_message(say)
    
    def _handle_process_command(self, command: dict, say: Say):
        """Handle /process command."""
        try:
            batch_id = command.get("text", "").strip()
            user_id = command["user_id"]
            
            if not batch_id:
                message = self.formatter.format_process_usage()
                say(**message)
                return
            
            # Mock batch validation
            if not self._validate_batch_access(batch_id, user_id):
                message = self.formatter.format_batch_not_found()
                say(**message)
                return
            
            # Start processing
            self._start_batch_processing(batch_id, user_id, say)
            
        except Exception as e:
            logger.error(f"Error in process command: {e}")
            self._send_error_message(say)
    
    def _handle_history_command(self, command: dict, say: Say):
        """Handle /history command."""
        try:
            user_id = command["user_id"]
            
            # Mock history data
            history = [
                {
                    "id": "batch_123",
                    "created_at": "2024-01-01T10:00:00Z",
                    "keyword_count": 50,
                    "status": "completed"
                },
                {
                    "id": "batch_124", 
                    "created_at": "2024-01-01T11:00:00Z",
                    "keyword_count": 30,
                    "status": "processing"
                }
            ]
            
            if not history:
                message = self.formatter.format_no_history()
            else:
                message = self.formatter.format_history(history)
            
            say(**message)
            
        except Exception as e:
            logger.error(f"Error in history command: {e}")
            self._send_error_message(say)
    
    def _handle_regenerate_command(self, command: dict, say: Say):
        """Handle /regenerate command."""
        try:
            batch_id = command.get("text", "").strip()
            user_id = command["user_id"]
            
            if not batch_id:
                message = self.formatter.format_regenerate_usage()
                say(**message)
                return
            
            if not self._validate_batch_access(batch_id, user_id):
                message = self.formatter.format_batch_not_found()
                say(**message)
                return
            
            # Start regeneration
            message = self.formatter.format_regeneration_started(batch_id)
            say(**message)
            
            # Simulate regeneration process
            self._simulate_regeneration(batch_id, say)
            
        except Exception as e:
            logger.error(f"Error in regenerate command: {e}")
            self._send_error_message(say)
    
    def _handle_start_processing_button(self, body: dict, say: Say):
        """Handle start processing button click."""
        try:
            action_value = body["actions"][0]["value"]
            batch_id = action_value.replace("process_", "")
            user_id = body["user"]["id"]
            
            # Start processing
            self._start_batch_processing(batch_id, user_id, say)
            
        except Exception as e:
            logger.error(f"Error handling start processing button: {e}")
            self._send_error_message(say)
    
    def _handle_process_keywords_button(self, body: dict, say: Say):
        """Handle process keywords button click."""
        try:
            user_id = body["user"]["id"]
            
            # Get original message text from the interaction
            original_message = body.get("message", {})
            text_block = None
            
            for block in original_message.get("blocks", []):
                if block.get("type") == "section":
                    text_element = block.get("text", {})
                    if "detected potential keywords" in text_element.get("text", ""):
                        # Extract keywords from the message
                        text_content = text_element.get("text", "")
                        # Simple extraction - in real implementation, store the original text
                        keywords_text = "sample keywords, content marketing, seo optimization"
                        self._process_keywords_from_text(keywords_text, user_id, say)
                        return
            
            # Fallback message
            say(**self.formatter.format_error_message())
            
        except Exception as e:
            logger.error(f"Error handling process keywords button: {e}")
            self._send_error_message(say)
    
    def _handle_ignore_keywords_button(self, body: dict):
        """Handle ignore keywords button click."""
        try:
            # Update the original message to remove buttons
            user_id = body["user"]["id"]
            logger.info(f"User {user_id} chose to ignore detected keywords")
            
        except Exception as e:
            logger.error(f"Error handling ignore keywords button: {e}")
    
    def _handle_file_upload(self, event: dict, say: Say):
        """Handle file upload events."""
        try:
            file_info = event["file"]
            user_id = event["user_id"]
            
            # Check if it's a CSV file
            if not file_info["name"].endswith(".csv"):
                return
            
            # Mock CSV processing
            say(**self.formatter.format_keywords_uploaded("batch_csv_123", 45))
            
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
    
    def _handle_message_keywords(self, event: dict, say: Say):
        """Handle messages that might contain keywords."""
        try:
            text = event.get("text", "")
            
            # Show keyword detection message
            message = self.formatter.format_keyword_detection(text[:100])
            say(**message)
            
        except Exception as e:
            logger.error(f"Error handling message keywords: {e}")
    
    def _handle_app_mention(self, event: dict, say: Say):
        """Handle app mentions."""
        try:
            message = self.formatter.format_help_message()
            say(**message)
            
        except Exception as e:
            logger.error(f"Error handling app mention: {e}")
    
    def _process_keywords_from_text(self, text: str, user_id: str, say: Say):
        """Process keywords from text input."""
        try:
            # Mock keyword processing
            keywords = [kw.strip() for kw in text.split(",") if kw.strip()]
            
            if not keywords:
                say(**self.formatter.format_no_keywords_found())
                return
            
            # Mock batch creation
            batch_id = f"batch_{len(keywords)}_{user_id[:8]}"
            
            # Send confirmation with action button
            message = self.formatter.format_keywords_uploaded(batch_id, len(keywords))
            say(**message)
            
            logger.info(f"Keywords processed: {len(keywords)} keywords for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing keywords from text: {e}")
            self._send_error_message(say)
    
    def _start_batch_processing(self, batch_id: str, user_id: str, say: Say):
        """Start processing a batch."""
        try:
            # Send processing started message
            message = self.formatter.format_processing_started(batch_id, 50)  # Mock count
            say(**message)
            
            # Simulate processing steps
            self._simulate_processing(batch_id, say)
            
        except Exception as e:
            logger.error(f"Error starting batch processing: {e}")
            self._send_error_message(say)
    
    def _simulate_processing(self, batch_id: str, say: Say):
        """Simulate the processing workflow."""
        import time
        import threading
        
        def process_in_background():
            try:
                # Step 1: Grouping
                time.sleep(2)
                say(**self.formatter.format_processing_step("Grouping keywords", 1, 4))
                
                # Step 2: Outlines
                time.sleep(3)
                say(**self.formatter.format_processing_step("Generating outlines", 2, 4))
                
                # Step 3: Post Ideas
                time.sleep(2)
                say(**self.formatter.format_processing_step("Generating post ideas", 3, 4))
                
                # Step 4: Report
                time.sleep(2)
                say(**self.formatter.format_processing_step("Generating report", 4, 4))
                
                # Completion
                time.sleep(1)
                download_url = f"/api/reports/{batch_id}/download"
                say(**self.formatter.format_processing_completed(batch_id, 5, 5, download_url))
                
                # Email notification
                say(**self.formatter.format_email_sent())
                
            except Exception as e:
                logger.error(f"Error in background processing: {e}")
                say(**self.formatter.format_processing_failed(batch_id))
        
        # Start background processing
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
    
    def _simulate_regeneration(self, batch_id: str, say: Say):
        """Simulate outline regeneration."""
        import time
        import threading
        
        def regenerate_in_background():
            try:
                time.sleep(3)  # Simulate processing time
                say(**self.formatter.format_regeneration_completed(batch_id))
            except Exception as e:
                logger.error(f"Error in regeneration: {e}")
        
        thread = threading.Thread(target=regenerate_in_background)
        thread.daemon = True
        thread.start()
    
    def _validate_batch_access(self, batch_id: str, user_id: str) -> bool:
        """Validate if user has access to the batch."""
        # Mock validation - in real implementation, check database
        return batch_id.startswith("batch_")
    
    def _might_contain_keywords(self, text: str) -> bool:
        """Check if text might contain keywords."""
        if not text or len(text) < 20:
            return False
        
        # Simple heuristics
        comma_count = text.count(",")
        newline_count = text.count("\n")
        
        return (comma_count > 2 and len(text.split(",")) > 3) or \
               (newline_count > 2 and len(text.split("\n")) > 3)
    
    def _send_error_message(self, say: Say):
        """Send generic error message."""
        say(**self.formatter.format_error_message())
