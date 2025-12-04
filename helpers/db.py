"""
Database module for TeraBox Downloader Bot
Handles MongoDB operations using Motor (async)
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any

from motor.motor_asyncio import AsyncIOMotorClient
import config
from helpers.logger import get_logger

logger = get_logger("terabox_bot")


class DatabaseManager:
    """MongoDB async database manager"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.users_collection = None
        self.logs_collection = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(config.MONGODB_URI)
            self.db = self.client[config.DATABASE_NAME]

            # Create collections and indexes
            self.users_collection = self.db["users"]
            self.logs_collection = self.db["logs"]

            # Create indexes
            await self.users_collection.create_index("user_id", unique=True)
            await self.logs_collection.create_index("timestamp")
            await self.logs_collection.create_index("user_id")

            # Test connection
            await self.client.admin.command("ping")
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            return await self.users_collection.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    async def create_user(self, user_id: int, first_name: str, last_name: Optional[str] = None):
        """Create new user record"""
        try:
            user_data = {
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name or "",
                "first_seen": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "total_requests": 0,
                "links_processed": 0,
                "last_bulk_count": 0,
                "downloaded_files": [],
            }
            result = await self.users_collection.insert_one(user_data)
            logger.info(f"Created new user: {user_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return None

    async def update_user(self, user_id: int, **updates):
        """Update user record"""
        try:
            update_data = {
                **updates,
                "last_active": datetime.utcnow(),
            }
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": update_data},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False

    async def increment_user_stats(self, user_id: int, links_count: int = 1):
        """Increment user statistics"""
        try:
            await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_requests": 1, "links_processed": links_count},
                    "$set": {"last_active": datetime.utcnow()},
                },
            )
        except Exception as e:
            logger.error(f"Error incrementing user stats for {user_id}: {e}")

    async def add_downloaded_file(self, user_id: int, file_info: Dict):
        """Add downloaded file to user's list"""
        try:
            file_data = {
                "file_name": file_info.get("file_name", ""),
                "file_size": file_info.get("file_size", ""),
                "size_bytes": file_info.get("size_bytes", 0),
                "download_link": file_info.get("download_link", ""),
                "timestamp": datetime.utcnow(),
            }
            await self.users_collection.update_one(
                {"user_id": user_id},
                {"$push": {"downloaded_files": file_data}},
            )
        except Exception as e:
            logger.error(f"Error adding downloaded file for user {user_id}: {e}")

    async def insert_log(self, log_entry: Dict):
        """Insert log entry to database"""
        try:
            log_entry["timestamp"] = datetime.utcnow()
            await self.logs_collection.insert_one(log_entry)
        except Exception as e:
            logger.error(f"Error inserting log: {e}")

    async def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get user statistics"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return None

            return {
                "total_requests": user.get("total_requests", 0),
                "links_processed": user.get("links_processed", 0),
                "first_seen": user.get("first_seen"),
                "last_active": user.get("last_active"),
                "downloaded_count": len(user.get("downloaded_files", [])),
            }
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return None

    async def get_recent_logs(self, user_id: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        try:
            query = {"user_id": user_id} if user_id else {}
            logs = (
                await self.logs_collection.find(query).sort("timestamp", -1).limit(limit).to_list(None)
            )
            return logs or []
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []


# Global database instance
db = DatabaseManager()
