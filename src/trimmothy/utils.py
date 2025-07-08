"""
Utility functions for Trimmothy video trimmer.

Contains shared functions for time conversion, file handling, and other common operations.
"""

import os
from pathlib import Path
from typing import Tuple


def seconds_to_time_string(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS string format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        String in HH:MM:SS format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def time_string_to_seconds(time_str: str) -> float:
    """
    Convert HH:MM:SS string to seconds.
    
    Args:
        time_str: Time string in HH:MM:SS format
        
    Returns:
        Time in seconds, or 0 if invalid format
    """
    try:
        parts = time_str.strip().split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            # Validate values
            if 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59:
                return hours * 3600 + minutes * 60 + seconds
        return 0
    except (ValueError, AttributeError):
        return 0


def validate_time_range(start_seconds: float, end_seconds: float, video_duration: float) -> Tuple[bool, str]:
    """
    Validate that a time range is valid for trimming.
    
    Args:
        start_seconds: Start time in seconds
        end_seconds: End time in seconds  
        video_duration: Total video duration in seconds
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if start_seconds < 0:
        return False, "Start time cannot be negative"
    
    if end_seconds > video_duration:
        return False, "End time cannot exceed video duration"
    
    if start_seconds >= end_seconds:
        return False, "Start time must be before end time"
    
    if end_seconds - start_seconds < 0.1:
        return False, "Trim duration too short (minimum 0.1 seconds)"
    
    return True, ""


def generate_output_filename(input_path: str, suffix: str = "--trimmothy") -> str:
    """
    Generate output filename with suffix.
    
    Args:
        input_path: Original video file path
        suffix: Suffix to add before file extension
        
    Returns:
        New filename with suffix
    """
    path = Path(input_path)
    stem = path.stem
    extension = path.suffix
    return f"{stem}{suffix}{extension}"


def ensure_directory_exists(file_path: str) -> bool:
    """
    Ensure the directory for a file path exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        directory = Path(file_path).parent
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB, or 0 if file doesn't exist
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0


def is_video_file(file_path: str) -> bool:
    """
    Check if file is a supported video format.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file extension indicates video format
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'}
    extension = Path(file_path).suffix.lower()
    return extension in video_extensions


def cleanup_temp_files(*file_paths: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        *file_paths: Variable number of file paths to delete
    """
    for file_path in file_paths:
        try:
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
        except Exception as e:
            print(f"Failed to cleanup {file_path}: {e}")


def format_duration(seconds: float) -> str:
    """
    Format duration in a human-readable way.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours" 