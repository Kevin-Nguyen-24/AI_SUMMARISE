"""
File validation utilities
"""
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings


def validate_file(file: UploadFile) -> Tuple[bool, str]:
    """
    Validate uploaded file based on size and extension
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not file.filename:
        return False, "No filename provided"
    
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in settings.allowed_extensions:
        return False, f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions)}"
    
    # Check file size (if available in headers)
    if hasattr(file, 'size') and file.size:
        if file.size > settings.max_file_size_bytes:
            return False, f"File too large. Maximum size: {settings.max_file_size_mb}MB"
    
    return True, ""


def get_file_extension(filename: str) -> str:
    """Extract file extension without the dot"""
    return Path(filename).suffix.lower().lstrip('.')
