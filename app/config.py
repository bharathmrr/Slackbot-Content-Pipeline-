"""
Configuration management for the Slackbot Content Pipeline.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Slackbot Content Pipeline"
    version: str = "1.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Slack Configuration
    slack_bot_token: str = Field(..., alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., alias="SLACK_SIGNING_SECRET")
    slack_app_token: Optional[str] = Field(None, alias="SLACK_APP_TOKEN")
    
    # Database
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_service_role_key: Optional[str] = Field(None, alias="SUPABASE_SERVICE_ROLE_KEY")
    
    # AI Services
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    
    # Search APIs
    serp_api_key: Optional[str] = Field(None, alias="SERP_API_KEY")
    brave_search_api_key: Optional[str] = Field(None, alias="BRAVE_SEARCH_API_KEY")
    
    # Redis Cache
    redis_url: Optional[str] = Field(None, alias="REDIS_URL")
    
    # Email
    sendgrid_api_key: Optional[str] = Field(None, alias="SENDGRID_API_KEY")
    from_email: Optional[str] = Field(None, alias="FROM_EMAIL")
    
    # Processing Configuration
    max_keywords_per_batch: int = Field(default=1000, alias="MAX_KEYWORDS_PER_BATCH")
    max_groups_per_batch: int = Field(default=20, alias="MAX_GROUPS_PER_BATCH")
    outline_generation_timeout: int = Field(default=30, alias="OUTLINE_GENERATION_TIMEOUT")
    
    # File Upload
    max_file_size: int = Field(default=10485760, alias="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: str = Field(default="text/csv,text/plain", alias="ALLOWED_FILE_TYPES")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=900, alias="RATE_LIMIT_WINDOW")  # 15 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def allowed_file_types_list(self) -> list[str]:
        """Get allowed file types as a list."""
        return [ft.strip() for ft in self.allowed_file_types.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
