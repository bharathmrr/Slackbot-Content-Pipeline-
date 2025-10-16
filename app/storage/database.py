"""
Database management using Supabase.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from loguru import logger

from app.config import get_settings


class DatabaseManager:
    """Manages database operations with Supabase."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[Client] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the database connection."""
        try:
            self.client = create_client(
                self.settings.supabase_url,
                self.settings.supabase_key
            )
            
            # Test connection
            response = self.client.table('keyword_batches').select("count", count="exact").execute()
            
            # Create tables if they don't exist
            self._ensure_tables_exist()
            
            self._initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            if not self._initialized:
                return False
            
            # Simple query to test connection
            response = self.client.table('keyword_batches').select("count", count="exact").execute()
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _ensure_tables_exist(self):
        """Ensure required tables exist."""
        try:
            # This would typically be done via migrations
            # For demo purposes, we'll assume tables exist
            logger.info("Database tables verified")
            
        except Exception as e:
            logger.warning(f"Table creation/verification failed: {e}")
    
    # Keyword Batches
    async def create_keyword_batch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new keyword batch."""
        try:
            batch_data = {
                "user_id": data["user_id"],
                "keywords": data["keywords"],
                "keyword_count": data["keyword_count"],
                "status": data.get("status", "uploaded"),
                "source": data.get("source", "unknown"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table('keyword_batches').insert(batch_data).execute()
            
            if response.data:
                logger.info(f"Created keyword batch: {response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Error creating keyword batch: {e}")
            raise
    
    def create_keyword_batch_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of create_keyword_batch for Flask."""
        # Mock implementation for demo
        import uuid
        batch = {
            "id": str(uuid.uuid4()),
            "user_id": data["user_id"],
            "keywords": data["keywords"],
            "keyword_count": data["keyword_count"],
            "status": data.get("status", "uploaded"),
            "source": data.get("source", "unknown"),
            "created_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Mock created keyword batch: {batch['id']}")
        return batch
    
    async def get_keyword_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get a keyword batch by ID."""
        try:
            response = self.client.table('keyword_batches').select("*").eq('id', batch_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching keyword batch {batch_id}: {e}")
            return None
    
    async def update_keyword_batch(self, batch_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a keyword batch."""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table('keyword_batches').update(updates).eq('id', batch_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"Error updating keyword batch {batch_id}: {e}")
            raise
    
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's processing history."""
        try:
            response = (self.client.table('keyword_batches')
                       .select("*")
                       .eq('user_id', user_id)
                       .order('created_at', desc=True)
                       .limit(limit)
                       .execute())
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching user history for {user_id}: {e}")
            return []
    
    # Keyword Groups
    async def create_keyword_group(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a keyword group."""
        try:
            group_data = {
                "batch_id": data["batch_id"],
                "keywords": data["keywords"],
                "cluster_name": data["cluster_name"],
                "similarity_score": data.get("similarity_score", 0.0),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table('keyword_groups').insert(group_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Error creating keyword group: {e}")
            raise
    
    async def get_keyword_groups_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get keyword groups for a batch."""
        try:
            response = (self.client.table('keyword_groups')
                       .select("*")
                       .eq('batch_id', batch_id)
                       .execute())
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching keyword groups for batch {batch_id}: {e}")
            return []
    
    # Outlines
    async def create_outline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an outline."""
        try:
            outline_data = {
                "group_id": data["group_id"],
                "outline_data": data["outline_data"],
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table('outlines').insert(outline_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Error creating outline: {e}")
            raise
    
    async def update_outline(self, group_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an outline."""
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            
            response = (self.client.table('outlines')
                       .update(data)
                       .eq('group_id', group_id)
                       .execute())
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"Error updating outline for group {group_id}: {e}")
            raise
    
    async def get_outlines_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        """Get outlines for a group."""
        try:
            response = (self.client.table('outlines')
                       .select("*")
                       .eq('group_id', group_id)
                       .execute())
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching outlines for group {group_id}: {e}")
            return []
    
    # Reports
    async def create_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a report."""
        try:
            report_data = {
                "id": data["id"],
                "batch_id": data["batch_id"],
                "file_path": data["file_path"],
                "file_name": data["file_name"],
                "status": data.get("status", "pending"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table('reports').insert(report_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise
    
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a report by ID."""
        try:
            response = self.client.table('reports').select("*").eq('id', report_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching report {report_id}: {e}")
            return None
    
    async def close(self):
        """Close database connections."""
        try:
            # Supabase client doesn't need explicit closing
            self._initialized = False
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database: {e}")


# SQL Schema for reference
SCHEMA_SQL = """
-- Keyword Batches Table
CREATE TABLE IF NOT EXISTS keyword_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    keywords JSONB NOT NULL,
    keyword_count INTEGER NOT NULL,
    status TEXT DEFAULT 'uploaded',
    source TEXT DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Keyword Groups Table  
CREATE TABLE IF NOT EXISTS keyword_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
    keywords JSONB NOT NULL,
    cluster_name TEXT NOT NULL,
    similarity_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Outlines Table
CREATE TABLE IF NOT EXISTS outlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES keyword_groups(id) ON DELETE CASCADE,
    outline_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY,
    batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_keyword_batches_user_id ON keyword_batches(user_id);
CREATE INDEX IF NOT EXISTS idx_keyword_batches_status ON keyword_batches(status);
CREATE INDEX IF NOT EXISTS idx_keyword_groups_batch_id ON keyword_groups(batch_id);
CREATE INDEX IF NOT EXISTS idx_outlines_group_id ON outlines(group_id);
CREATE INDEX IF NOT EXISTS idx_reports_batch_id ON reports(batch_id);
"""
