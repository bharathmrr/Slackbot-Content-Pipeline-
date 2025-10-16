"""
Slack bot implementation for the Content Pipeline.
"""

import asyncio
from typing import Optional

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from loguru import logger

from app.config import get_settings
from app.slack.commands import CommandHandler
from app.slack.formatter import MessageFormatter
from app.storage.database import DatabaseManager
from app.storage.cache import CacheManager


class SlackBot:
    """Main Slack bot class."""
    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.settings = get_settings()
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        
        # Initialize Slack app
        self.app = AsyncApp(
            token=self.settings.slack_bot_token,
            signing_secret=self.settings.slack_signing_secret
        )
        
        # Initialize components
        self.command_handler = CommandHandler(db_manager, cache_manager)
        self.formatter = MessageFormatter()
        
        # Socket mode handler for real-time events
        self.handler: Optional[AsyncSocketModeHandler] = None
        if self.settings.slack_app_token:
            self.handler = AsyncSocketModeHandler(
                self.app, 
                self.settings.slack_app_token
            )
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all Slack event handlers."""
        
        # Slash commands
        @self.app.command("/keywords")
        async def handle_keywords_command(ack, command, client):
            await ack()
            await self.command_handler.handle_keywords_command(command, client)
        
        @self.app.command("/process")
        async def handle_process_command(ack, command, client):
            await ack()
            await self.command_handler.handle_process_command(command, client)
        
        @self.app.command("/history")
        async def handle_history_command(ack, command, client):
            await ack()
            await self.command_handler.handle_history_command(command, client)
        
        @self.app.command("/regenerate")
        async def handle_regenerate_command(ack, command, client):
            await ack()
            await self.command_handler.handle_regenerate_command(command, client)
        
        # File upload events
        @self.app.event("file_shared")
        async def handle_file_shared(event, client):
            await self.command_handler.handle_file_upload(event, client)
        
        # Message events for keyword detection
        @self.app.event("message")
        async def handle_message(event, client):
            # Only process messages that might contain keywords
            if self._might_contain_keywords(event.get("text", "")):
                await self.command_handler.handle_message_keywords(event, client)
        
        # App mention events
        @self.app.event("app_mention")
        async def handle_app_mention(event, client):
            await self.command_handler.handle_app_mention(event, client)
        
        # Error handler
        @self.app.error
        async def handle_errors(error, body, logger_inner):
            logger.error(f"Slack error: {error}")
            logger.debug(f"Error body: {body}")
    
    def _might_contain_keywords(self, text: str) -> bool:
        """Check if a message might contain keywords."""
        if not text or len(text) < 10:
            return False
        
        # Simple heuristics to detect keyword lists
        indicators = [
            "," in text and len(text.split(",")) > 2,  # Comma-separated
            "\n" in text and len(text.split("\n")) > 2,  # Line-separated
            "keyword" in text.lower(),
            "seo" in text.lower(),
            "content" in text.lower()
        ]
        
        return any(indicators)
    
    async def start(self):
        """Start the Slack bot."""
        try:
            if self.handler:
                logger.info("Starting Slack bot in Socket Mode...")
                await self.handler.start_async()
            else:
                logger.warning("Socket Mode not configured. Bot will only respond to HTTP requests.")
                # Keep the event loop running
                while True:
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Failed to start Slack bot: {e}")
            raise
    
    async def stop(self):
        """Stop the Slack bot."""
        try:
            if self.handler:
                await self.handler.close_async()
            logger.info("Slack bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Slack bot: {e}")
    
    async def send_message(self, channel: str, text: str, **kwargs):
        """Send a message to a Slack channel."""
        try:
            response = await self.app.client.chat_postMessage(
                channel=channel,
                text=text,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Failed to send message to {channel}: {e}")
            raise
    
    async def send_formatted_message(self, channel: str, message_data: dict):
        """Send a formatted message using the formatter."""
        formatted = self.formatter.format_message(message_data)
        return await self.send_message(channel, **formatted)
