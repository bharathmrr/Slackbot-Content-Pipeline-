#!/usr/bin/env python3
"""
Flask application runner for the Slackbot Content Pipeline.
"""

import os
import sys
from loguru import logger

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main_flask import app
from app.config import get_settings


def setup_logging():
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # File logging
    logger.add(
        "logs/app.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )


def main():
    """Main entry point."""
    # Setup logging
    setup_logging()
    
    # Load settings
    settings = get_settings()
    
    logger.info("Starting Slackbot Content Pipeline (Flask)")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Host: {settings.host}")
    logger.info(f"Port: {settings.port}")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    try:
        # Run the Flask app
        app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.is_development,
            threaded=True,
            use_reloader=False  # Disable reloader to avoid issues with threading
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
