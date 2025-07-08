"""
FFmpeg-based video processing module for Trimmothy.

This module handles all video operations using FFmpeg directly,
providing better reliability and performance than MoviePy.
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, Tuple, Optional, Callable
import tempfile
import os


class VideoProcessor:
    """Handles video processing operations using FFmpeg."""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
        
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable path."""
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
        return ffmpeg_path
        
    def _find_ffprobe(self) -> str:
        """Find FFprobe executable path."""
        ffprobe_path = shutil.which('ffprobe')
        if not ffprobe_path:
            raise RuntimeError("FFprobe not found. Please install FFmpeg.")
        return ffprobe_path
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get comprehensive video information using FFprobe.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing video information
        """
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            audio_stream = None
            
            for stream in data['streams']:
                if stream['codec_type'] == 'video' and not video_stream:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and not audio_stream:
                    audio_stream = stream
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # Calculate duration and frame info
            duration = float(data['format']['duration'])
            fps = eval(video_stream['r_frame_rate'])  # e.g., "30000/1001"
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            frame_count = int(float(video_stream.get('nb_frames', duration * fps)))
            
            return {
                'duration': duration,
                'fps': fps,
                'width': width,
                'height': height,
                'frame_count': frame_count,
                'video_codec': video_stream['codec_name'],
                'audio_codec': audio_stream['codec_name'] if audio_stream else None,
                'format': data['format']['format_name'],
                'video_stream': video_stream,
                'audio_stream': audio_stream
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFprobe failed: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Failed to get video info: {e}")
    
    def trim_video(self, 
                   input_path: str, 
                   output_path: str, 
                   start_time: float, 
                   end_time: float,
                   progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        """
        Trim video using FFmpeg with smart codec handling.
        
        Args:
            input_path: Input video file path
            output_path: Output video file path  
            start_time: Start time in seconds
            end_time: End time in seconds
            progress_callback: Optional callback for progress updates (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            duration = end_time - start_time
            
            # Get video info to determine best approach
            video_info = self.get_video_info(input_path)
            
            # Try different encoding strategies in order of speed
            strategies = [
                self._try_stream_copy,
                self._try_video_copy_audio_reencode,
                self._try_fast_reencode,
                self._try_compatible_reencode
            ]
            
            for strategy in strategies:
                try:
                    if progress_callback:
                        progress_callback(0.1)
                    
                    success = strategy(input_path, output_path, start_time, duration, video_info, progress_callback)
                    if success:
                        if progress_callback:
                            progress_callback(1.0)
                        return True
                except Exception as e:
                    print(f"Strategy {strategy.__name__} failed: {e}")
                    # Clean up partial file
                    if Path(output_path).exists():
                        Path(output_path).unlink()
                    continue
            
            return False
            
        except Exception as e:
            print(f"Trim video failed: {e}")
            return False
    
    def _try_stream_copy(self, input_path: str, output_path: str, start_time: float, 
                        duration: float, video_info: Dict, progress_callback: Optional[Callable] = None) -> bool:
        """Try full stream copy (fastest)."""
        cmd = [
            self.ffmpeg_path,
            '-y',  # Overwrite output
            '-ss', str(start_time),
            '-i', input_path,
            '-t', str(duration),
            '-c', 'copy',  # Copy all streams
            '-avoid_negative_ts', 'make_zero',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _try_video_copy_audio_reencode(self, input_path: str, output_path: str, start_time: float,
                                     duration: float, video_info: Dict, progress_callback: Optional[Callable] = None) -> bool:
        """Try video copy with audio re-encode."""
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-ss', str(start_time),
            '-i', input_path,
            '-t', str(duration),
            '-c:v', 'copy',  # Copy video stream
            '-c:a', 'aac',   # Re-encode audio to AAC
            '-b:a', '128k',  # Audio bitrate
            '-avoid_negative_ts', 'make_zero',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _try_fast_reencode(self, input_path: str, output_path: str, start_time: float,
                          duration: float, video_info: Dict, progress_callback: Optional[Callable] = None) -> bool:
        """Try fast re-encoding."""
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-ss', str(start_time),
            '-i', input_path,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _try_compatible_reencode(self, input_path: str, output_path: str, start_time: float,
                                duration: float, video_info: Dict, progress_callback: Optional[Callable] = None) -> bool:
        """Try maximum compatibility re-encoding."""
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-ss', str(start_time),
            '-i', input_path,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def extract_frame(self, video_path: str, time_seconds: float, output_path: str, width: int = 400, height: int = 300) -> bool:
        """
        Extract a single frame from video at specified time.
        
        Args:
            video_path: Input video path
            time_seconds: Time in seconds to extract frame
            output_path: Output image path
            width: Output width
            height: Output height
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                self.ffmpeg_path,
                '-y',
                '-ss', str(time_seconds),
                '-i', video_path,
                '-vframes', '1',
                '-vf', f'scale={width}:{height}',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Frame extraction failed: {e}")
            return False
    
    def extract_thumbnails(self, video_path: str, output_dir: str, count: int = 8, width: int = 120, height: int = 80) -> list:
        """
        Extract thumbnail images from video at regular intervals.
        
        Args:
            video_path: Input video path
            output_dir: Directory for thumbnail images
            count: Number of thumbnails to extract
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            List of thumbnail file paths
        """
        try:
            video_info = self.get_video_info(video_path)
            duration = video_info['duration']
            
            thumbnails = []
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            for i in range(count):
                time_pos = (i * duration) / (count - 1) if count > 1 else 0
                if i == count - 1:  # Last thumbnail should be at end
                    time_pos = duration - 1
                
                thumb_path = output_path / f"thumb_{i:03d}.jpg"
                
                if self.extract_frame(video_path, time_pos, str(thumb_path), width, height):
                    thumbnails.append(str(thumb_path))
            
            return thumbnails
            
        except Exception as e:
            print(f"Thumbnail extraction failed: {e}")
            return [] 