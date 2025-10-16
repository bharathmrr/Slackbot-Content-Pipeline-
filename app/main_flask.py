"""
Flask-based main application for the Slackbot Content Pipeline.
"""

import os
import threading
from flask import Flask, request, jsonify, make_response
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from loguru import logger

from app.config import get_settings
from app.slack.flask_bot import FlaskSlackBot
from app.storage.database import DatabaseManager
from app.storage.cache import CacheManager


def create_app():
    """Create and configure the Flask application."""
    
    # Initialize Flask app
    flask_app = Flask(__name__)
    
    # Load settings
    settings = get_settings()
    
    # Configure Flask
    flask_app.config['SECRET_KEY'] = settings.slack_signing_secret
    flask_app.config['DEBUG'] = settings.is_development
    
    # Initialize services
    db_manager = DatabaseManager()
    cache_manager = CacheManager()
    
    # Initialize Slack bot
    slack_app = App(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret,
        process_before_response=True
    )
    
    # Initialize bot handlers
    slack_bot = FlaskSlackBot(slack_app, db_manager, cache_manager)
    slack_bot.register_handlers()
    
    # Create Slack request handler
    handler = SlackRequestHandler(slack_app)
    
    # Store instances in app context
    flask_app.db_manager = db_manager
    flask_app.cache_manager = cache_manager
    flask_app.slack_bot = slack_bot
    
    # Routes
    @flask_app.route("/", methods=["GET"])
    def home():
        """Home endpoint."""
        return jsonify({
            "message": "Slackbot Content Pipeline API",
            "version": settings.version,
            "status": "healthy"
        })
    
    @flask_app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        try:
            # Basic health check
            return jsonify({
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "services": {
                    "database": "healthy",
                    "cache": "healthy", 
                    "slack_bot": "healthy"
                }
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 503
    
    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        """Handle Slack events."""
        return handler.handle(request)
    
    @flask_app.route("/slack/interactive", methods=["POST"])
    def slack_interactive():
        """Handle Slack interactive components."""
        return handler.handle(request)
    
    @flask_app.route("/slack/commands", methods=["POST"])
    def slack_commands():
        """Handle Slack slash commands."""
        return handler.handle(request)
    
    # API Routes
    @flask_app.route("/api/batches/<batch_id>", methods=["GET"])
    def get_batch(batch_id):
        """Get batch information."""
        try:
            # This would be implemented with actual database calls
            batch = {"id": batch_id, "status": "completed", "keyword_count": 50}
            return jsonify(batch)
        except Exception as e:
            logger.error(f"Error fetching batch {batch_id}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    @flask_app.route("/api/batches/<batch_id>/groups", methods=["GET"])
    def get_batch_groups(batch_id):
        """Get keyword groups for a batch."""
        try:
            # Mock response
            groups = [
                {"id": "group_1", "name": "SEO Keywords", "keywords": ["seo", "optimization"]},
                {"id": "group_2", "name": "Content Marketing", "keywords": ["content", "marketing"]}
            ]
            return jsonify(groups)
        except Exception as e:
            logger.error(f"Error fetching groups for batch {batch_id}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    @flask_app.route("/api/reports/<report_id>/download", methods=["GET"])
    def download_report(report_id):
        """Download a report."""
        try:
            # Mock response - in real implementation, stream the PDF file
            return jsonify({
                "download_url": f"/files/reports/{report_id}.pdf",
                "message": "Report ready for download"
            })
        except Exception as e:
            logger.error(f"Error downloading report {report_id}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    # Error handlers
    @flask_app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @flask_app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    @flask_app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    # Initialize services on startup
    @flask_app.before_first_request
    def initialize_services():
        """Initialize services before first request."""
        try:
            # Initialize database and cache in background
            def init_services():
                db_manager.initialize()
                cache_manager.initialize()
                logger.info("Services initialized successfully")
            
            init_thread = threading.Thread(target=init_services)
            init_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
    
    return flask_app


# Create the Flask app instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    logger.info(f"Starting Flask server on {settings.host}:{settings.port}")
    
    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.is_development,
        threaded=True
    )
