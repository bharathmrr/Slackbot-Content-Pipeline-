"""
Main application entry point for the Slackbot Content Pipeline.
"""

import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import get_settings
from app.slack.bot import SlackBot
from app.storage.database import DatabaseManager
from app.storage.cache import CacheManager


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Slackbot Content Pipeline...")
    
    # Initialize services
    try:
        # Initialize database
        db_manager = DatabaseManager()
        await db_manager.initialize()
        app.state.db = db_manager
        
        # Initialize cache
        cache_manager = CacheManager()
        await cache_manager.initialize()
        app.state.cache = cache_manager
        
        # Initialize and start Slack bot in a separate thread
        slack_bot = SlackBot(db_manager, cache_manager)
        
        def run_slack_bot():
            asyncio.run(slack_bot.start())
        
        slack_thread = threading.Thread(target=run_slack_bot, daemon=True)
        slack_thread.start()
        app.state.slack_bot = slack_bot
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    try:
        if hasattr(app.state, 'slack_bot'):
            await app.state.slack_bot.stop()
        if hasattr(app.state, 'cache'):
            await app.state.cache.close()
        if hasattr(app.state, 'db'):
            await app.state.db.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A comprehensive Slackbot for keyword-based content creation",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Slackbot Content Pipeline API",
        "version": settings.version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        if hasattr(app.state, 'db'):
            await app.state.db.health_check()
        
        # Check cache connection
        if hasattr(app.state, 'cache'):
            await app.state.cache.health_check()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "database": "healthy",
                "cache": "healthy",
                "slack_bot": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/api/batches/{batch_id}")
async def get_batch(batch_id: str):
    """Get batch information."""
    try:
        batch = await app.state.db.get_keyword_batch(batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        return batch
    except Exception as e:
        logger.error(f"Error fetching batch {batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/batches/{batch_id}/groups")
async def get_batch_groups(batch_id: str):
    """Get keyword groups for a batch."""
    try:
        groups = await app.state.db.get_keyword_groups_by_batch(batch_id)
        return groups
    except Exception as e:
        logger.error(f"Error fetching groups for batch {batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: str):
    """Download a report."""
    try:
        report = await app.state.db.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # In a real implementation, you would stream the file
        return {"download_url": f"/files/reports/{report_id}.pdf"}
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.is_development
    )
