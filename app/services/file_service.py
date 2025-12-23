"""
File upload and management service
"""
import os
import uuid
import logging
from pathlib import Path
from fastapi import UploadFile
from app.config import settings


logger = logging.getLogger(__name__)


class FileService:
    """Handle file uploads and temporary storage"""
    
    def __init__(self, upload_dir: Path = None):
        """
        Initialize file service
        
        Args:
            upload_dir: Directory for temporary file storage
        """
        self.upload_dir = upload_dir or settings.upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, file: UploadFile) -> Path:
        """
        Save uploaded file to temporary directory
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Path to saved file
            
        Raises:
            Exception: If file save fails
        """
        try:
            # Generate unique filename to avoid collisions
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = self.upload_dir / unique_filename
            
            # Read and save file
            content = await file.read()
            
            # Check actual file size
            file_size = len(content)
            if file_size > settings.max_file_size_bytes:
                raise ValueError(f"File too large: {file_size} bytes (max: {settings.max_file_size_bytes})")
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"Saved file: {file.filename} -> {file_path} ({file_size} bytes)")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise Exception(f"Failed to save uploaded file: {str(e)}")
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete temporary file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old temporary files
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        import time
        
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        self.delete_file(file_path)
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old files")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
