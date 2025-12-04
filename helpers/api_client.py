"""
API Client module for TeraBox Downloader Bot
Handles API requests to TeraBox resolver
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any
import json

import config
from helpers.logger import get_logger

logger = get_logger("terabox_bot")


class TeraBoxAPI:
    """TeraBox API client"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=config.API_TIMEOUT)

    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.info("API session initialized")

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            logger.info("API session closed")

    async def resolve_link(self, terabox_link: str) -> Optional[Dict[str, Any]]:
        """
        Resolve TeraBox link and get file information

        Args:
            terabox_link: TeraBox link to resolve

        Returns:
            Dictionary with file info or None on failure
        """
        if not self.session:
            await self.init_session()

        for attempt in range(config.MAX_RETRIES):
            try:
                params = {"url": terabox_link}
                async with self.session.get(config.TERABOX_API, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Validate response - status could be "Successfully" or "✅ Successfully"
                        api_status = data.get("status", "").strip()
                        has_download_link = data.get("download_link") or data.get("server_filename")
                        
                        if ("Successfully" in api_status or "success" in api_status.lower()) and has_download_link:
                            logger.debug(f"Successfully resolved: {terabox_link}")
                            return {
                                "file_name": data.get("file_name") or data.get("server_filename", "unknown"),
                                "file_size": data.get("file_size", "0 B"),
                                "size_bytes": int(data.get("size_bytes", 0)),
                                "download_link": data.get("download_link", ""),
                                "thumbnail": data.get("thumbnail", ""),
                                "proxy_url": data.get("proxy_url", ""),
                            }
                        else:
                            logger.warning(f"API error for {terabox_link}: {api_status} | has_link: {has_download_link}")
                            return None
                    elif response.status == 429:
                        # Rate limited
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"API returned status {response.status} for {terabox_link}")
                        return None

            except asyncio.TimeoutError:
                logger.warning(f"API timeout for {terabox_link} (attempt {attempt + 1}/{config.MAX_RETRIES})")
                if attempt < config.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None

            except aiohttp.ClientError as e:
                logger.error(f"API client error for {terabox_link}: {e}")
                if attempt < config.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response for {terabox_link}")
                return None

            except Exception as e:
                logger.error(f"Unexpected error resolving {terabox_link}: {e}", exc_info=True)
                return None

        logger.error(f"Failed to resolve {terabox_link} after {config.MAX_RETRIES} attempts")
        return None

    async def validate_link(self, link: str) -> bool:
        """Check if link is a valid TeraBox link"""
        import re

        for pattern in config.TERABOX_DOMAINS:
            if re.match(pattern, link):
                return True
        return False


# Global API client instance
api_client = TeraBoxAPI()
