"""
Metadata extraction module for TeraBox Downloader Bot
Handles video metadata and thumbnail generation
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import json
from PIL import Image
import io

import config
from helpers.logger import get_logger

logger = get_logger("terabox_bot")


class MetadataExtractor:
    """Extract metadata from media files"""

    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
        self.ffprobe_available = self._check_ffprobe()

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            logger.info("ffmpeg is available")
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ffmpeg not found")
            return False

    def _check_ffprobe(self) -> bool:
        """Check if ffprobe is available"""
        try:
            subprocess.run(["ffprobe", "-version"], capture_output=True, timeout=5)
            logger.info("ffprobe is available")
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ffprobe not found")
            return False

    async def extract_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from file using ffprobe

        Args:
            file_path: Path to media file

        Returns:
            Dictionary with metadata or None on failure
        """
        if not self.ffprobe_available or not config.ENABLE_METADATA_EXTRACTION:
            return self._get_basic_metadata(file_path)

        try:
            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(None, self._run_ffprobe, file_path)
            return metadata or self._get_basic_metadata(file_path)
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return self._get_basic_metadata(file_path)

    def _run_ffprobe(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Run ffprobe and extract metadata"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "format=duration:stream=width,height,codec_name",
                "-of", "json",
                str(file_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.FFMPEG_TIMEOUT)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return self._parse_ffprobe_output(data, file_path)
            return None
        except Exception as e:
            logger.error(f"ffprobe execution error: {e}")
            return None

    def _parse_ffprobe_output(self, data: Dict, file_path: Path) -> Dict[str, Any]:
        """Parse ffprobe output"""
        metadata = {
            "file_name": file_path.name,
            "file_size": self._format_size(file_path.stat().st_size),
            "duration": 0,
            "resolution": "Unknown",
            "codec": "Unknown",
        }

        # Extract format info
        if "format" in data and "duration" in data["format"]:
            try:
                duration = float(data["format"]["duration"])
                metadata["duration"] = self._format_duration(duration)
            except (ValueError, TypeError):
                pass

        # Extract stream info
        if "streams" in data and data["streams"]:
            stream = data["streams"][0]
            width = stream.get("width", 0)
            height = stream.get("height", 0)
            if width and height:
                metadata["resolution"] = f"{width}x{height}"
            codec = stream.get("codec_name", "Unknown")
            metadata["codec"] = codec.upper()

        return metadata

    def _get_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get basic metadata without ffprobe"""
        return {
            "file_name": file_path.name,
            "file_size": self._format_size(file_path.stat().st_size),
            "duration": "N/A",
            "resolution": "N/A",
            "codec": "N/A",
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        return f"{minutes}m {secs}s"

    async def generate_thumbnail(
        self,
        file_path: Path,
        output_path: Path,
        size: tuple = config.THUMBNAIL_SIZE,
    ) -> Optional[Path]:
        """
        Generate thumbnail for video file

        Args:
            file_path: Path to media file
            output_path: Path to save thumbnail
            size: Thumbnail size (width, height)

        Returns:
            Path to generated thumbnail or None on failure
        """
        if not self.ffmpeg_available or not config.ENABLE_THUMBNAIL_GENERATION:
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._run_ffmpeg_thumbnail, file_path, output_path, size
            )
            return result
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None

    def _run_ffmpeg_thumbnail(self, file_path: Path, output_path: Path, size: tuple) -> Optional[Path]:
        """Run ffmpeg to generate thumbnail"""
        try:
            cmd = [
                "ffmpeg",
                "-i", str(file_path),
                "-ss", "00:00:01",
                "-vf", f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
                "-vframes", "1",
                "-y",
                str(output_path),
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=config.FFMPEG_TIMEOUT)

            if result.returncode == 0 and output_path.exists():
                logger.info(f"Generated thumbnail: {output_path}")
                return output_path
            return None
        except Exception as e:
            logger.error(f"ffmpeg thumbnail execution error: {e}")
            return None


# Global metadata extractor instance
metadata_extractor = MetadataExtractor()
