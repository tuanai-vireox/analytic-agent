"""
File utility functions for handling uploads and file operations.
"""

import os
import aiofiles
from typing import List
from fastapi import UploadFile, HTTPException
from app.config import settings


ALLOWED_FILE_TYPES = {
    "csv": ["text/csv", "application/csv"],
    "json": ["application/json"],
    "xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    "xls": ["application/vnd.ms-excel"],
    "txt": ["text/plain"]
}

ALLOWED_EXTENSIONS = list(ALLOWED_FILE_TYPES.keys())


def validate_file_type(file: UploadFile) -> bool:
    """
    Validate if the uploaded file type is allowed.
    
    Args:
        file: Uploaded file
        
    Returns:
        True if file type is allowed
    """
    if not file.filename:
        return False
    
    # Check file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type
    if file.content_type not in ALLOWED_FILE_TYPES.get(file_extension, []):
        return False
    
    return True


async def save_upload_file(file: UploadFile, filename: str = None) -> str:
    """
    Save uploaded file to the upload directory.
    
    Args:
        file: Uploaded file
        filename: Optional custom filename
        
    Returns:
        Path to saved file
    """
    if not validate_file_type(file):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        filename = file.filename
    
    file_path = os.path.join(settings.upload_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def delete_file(file_path: str) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if file was deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def list_uploaded_files() -> List[str]:
    """
    List all files in the upload directory.
    
    Returns:
        List of filenames
    """
    if not os.path.exists(settings.upload_dir):
        return []
    
    files = []
    for filename in os.listdir(settings.upload_dir):
        file_path = os.path.join(settings.upload_dir, filename)
        if os.path.isfile(file_path):
            files.append(filename)
    
    return files 