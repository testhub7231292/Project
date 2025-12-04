"""
Downloader module for TeraBox Downloader Bot
Handles file downloads with progress tracking
"""

import aiohttp
import asyncio
from pathlib import Path
from typing import Optional, Callable
import mimetypes

import config
from helpers.logger import get_logger

logger = get_logger("terabox_bot")


class FileDownloader:
    """Async file downloader with progress tracking"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=config.DOWNLOAD_TIMEOUT)
        self.downloads_dir = config.DOWNLOAD_DIR
        self.downloads_dir.mkdir(exist_ok=True)

    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def download(
        self,
        url: str,
        file_name: str,
        progress_callback: Optional[Callable] = None,
    ) -> Optional[Path]:
        """
        Download file from URL

        Args:
            url: Download URL
            file_name: Local filename to save as
            progress_callback: Async callback for progress updates

        Returns:
            Path to downloaded file or None on failure
        """
        if not self.session:
            await self.init_session()

        file_path = self.downloads_dir / file_name

        try:
            # Check if file already exists
            if file_path.exists():
                logger.warning(f"File already exists: {file_path}")
                return file_path

            logger.info(f"Starting download: {file_name}")

            async with self.session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    logger.error(f"Download failed with status {response.status}: {url}")
                    return None

                total_size = int(response.headers.get("content-length", 0))

                # Check file size limits
                if total_size > config.SIZE_LIMIT_CHANNEL_MB * 1024 * 1024:
                    logger.error(f"File too large ({total_size} bytes): {file_name}")
                    return None

                downloaded_size = 0

                with open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(config.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # Report progress
                            if progress_callback and total_size > 0:
                                percentage = (downloaded_size / total_size) * 100
                                await progress_callback(percentage, downloaded_size, total_size)

                logger.info(f"Download completed: {file_name} ({downloaded_size} bytes)")
                return file_path

        except asyncio.TimeoutError:
            logger.error(f"Download timeout: {file_name}")
            self._cleanup_file(file_path)
            return None

        except aiohttp.ClientError as e:
            logger.error(f"Download client error: {e}")
            self._cleanup_file(file_path)
            return None

        except Exception as e:
            logger.error(f"Download error: {e}", exc_info=True)
            self._cleanup_file(file_path)
            return None

    def _cleanup_file(self, file_path: Path):
        """Remove downloaded file if cleanup is enabled"""
        if config.CLEANUP_DOWNLOADS and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup {file_path}: {e}")

    async def cleanup_all(self):
        """Clean up all downloaded files"""
        if not config.CLEANUP_DOWNLOADS:
            return

        try:
            for file in self.downloads_dir.iterdir():
                if file.is_file():
                    file.unlink()
                    logger.debug(f"Cleaned up: {file}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in MB"""
        if file_path.exists():
            return file_path.stat().st_size / (1024 * 1024)
        return 0

    def get_file_size_str(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def get_mime_type(self, file_path: Path) -> str:
        """Get MIME type of file"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"


# Global downloader instance
downloader = FileDownloader()
