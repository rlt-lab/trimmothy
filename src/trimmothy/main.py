import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import threading
import time
import tempfile
from pathlib import Path

# Import our modular components
from .video_processor import VideoProcessor
from .utils import (
    seconds_to_time_string, 
    time_string_to_seconds, 
    validate_time_range,
    generate_output_filename,
    ensure_directory_exists,
    is_video_file,
    cleanup_temp_files
)

# Set appearance mode and color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TrimmothyApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Trimmothy - Video Trimmer")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Video-related attributes
        self.video_path = None
        self.video_processor = VideoProcessor()
        self.video_info = None
        self.video_duration = 0
        self.current_frame = 0
        self.cap = None
        self.total_frames = 0
        self.fps = 30
        self.temp_dir = None
        
        # Trim settings
        self.trim_start = 0
        self.trim_end = 0
        
        # Playback settings
        self.is_playing = False
        self.playback_timer = None
        self.playback_speed = 30  # FPS for playback
        self._preview_mode = False
        self._preview_end_frame = 0
        
        # GUI elements
        self.video_label = None
        self.progress_slider = None
        self.start_time_var = None
        self.end_time_var = None
        self.play_button = None
        self.current_time_label = None
        self.start_time_display = None
        self.end_time_display = None
        self.thumbnail_frame = None
        self.thumbnail_images = []
        self.thumbnail_labels = []
        self.thumbnail_count = 8
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Trimmothy Video Trimmer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 20))
        
        self.file_label = ctk.CTkLabel(file_frame, text="No video file selected")
        self.file_label.pack(side="left", padx=20, pady=10)
        
        open_button = ctk.CTkButton(
            file_frame, 
            text="Open Video File", 
            command=self.open_video_file
        )
        open_button.pack(side="right", padx=20, pady=10)
        
        # Main content frame (horizontal split)
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left side - Video preview and playback controls
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Video preview frame
        self.video_frame = ctk.CTkFrame(left_frame)
        self.video_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        self.video_label = ctk.CTkLabel(
            self.video_frame, 
            text="Open a video file to begin trimming",
            font=ctk.CTkFont(size=16)
        )
        self.video_label.pack(expand=True)
        
        # Video controls frame (under video)
        video_controls_frame = ctk.CTkFrame(left_frame)
        video_controls_frame.pack(fill="x", pady=(0, 10))
        
        # Play/Pause button
        self.play_button = ctk.CTkButton(
            video_controls_frame,
            text="▶ Play",
            command=self.toggle_playback,
            width=100
        )
        self.play_button.pack(side="left", padx=10, pady=10)
        
        # Current time display
        self.current_time_label = ctk.CTkLabel(
            video_controls_frame,
            text="00:00:00"
        )
        self.current_time_label.pack(side="left", padx=(10, 5), pady=10)
        
        # Video progress slider with thumbnails
        progress_frame = ctk.CTkFrame(left_frame)
        progress_frame.pack(fill="x")
        
        progress_label = ctk.CTkLabel(progress_frame, text="Video Timeline:")
        progress_label.pack(pady=(10, 5))
        
        # Thumbnail progress bar frame
        self.thumbnail_frame = ctk.CTkFrame(progress_frame)
        self.thumbnail_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        # Regular slider (still needed for functionality)
        self.progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0,
            to=100,
            command=self.on_progress_change,
            height=30
        )
        self.progress_slider.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_slider.set(0)
        
        # Time labels under slider
        time_labels_frame = ctk.CTkFrame(progress_frame)
        time_labels_frame.pack(fill="x", padx=10)
        
        self.start_time_display = ctk.CTkLabel(time_labels_frame, text="00:00:00")
        self.start_time_display.pack(side="left")
        
        self.end_time_display = ctk.CTkLabel(time_labels_frame, text="00:00:00")
        self.end_time_display.pack(side="right")
        
        # Initialize thumbnail variables
        self.thumbnail_images = []
        self.thumbnail_labels = []
        self.thumbnail_count = 8  # Number of thumbnails to show
        
        # Right side - Trim controls and actions
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=False, padx=(10, 0))
        right_frame.configure(width=400)  # Fixed width for controls
        
        # Trim controls frame (right side)
        trim_frame = ctk.CTkFrame(right_frame)
        trim_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Trim selection label with current selection info
        self.trim_info_label = ctk.CTkLabel(trim_frame, text="Trim Selection: Full Video")
        self.trim_info_label.pack(pady=(10, 5))
        
        # Start and End sliders frame
        sliders_frame = ctk.CTkFrame(trim_frame)
        sliders_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Start trim slider
        start_slider_label = ctk.CTkLabel(sliders_frame, text="Start:")
        start_slider_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.start_trim_slider = ctk.CTkSlider(
            sliders_frame,
            from_=0,
            to=100,
            command=self.on_start_trim_change
        )
        self.start_trim_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.start_trim_slider.set(0)
        
        # End trim slider
        end_slider_label = ctk.CTkLabel(sliders_frame, text="End:")
        end_slider_label.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.end_trim_slider = ctk.CTkSlider(
            sliders_frame,
            from_=0,
            to=100,
            command=self.on_end_trim_change
        )
        self.end_trim_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.end_trim_slider.set(100)
        
        # Configure grid weights
        sliders_frame.grid_columnconfigure(1, weight=1)
        
        # Time input frame
        time_frame = ctk.CTkFrame(trim_frame)
        time_frame.pack(fill="x", pady=10)
        
        # Start time input
        start_label = ctk.CTkLabel(time_frame, text="Start Time (HH:MM:SS):")
        start_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.start_time_var = tk.StringVar(value="00:00:00")
        start_entry = ctk.CTkEntry(time_frame, textvariable=self.start_time_var, width=100)
        start_entry.grid(row=0, column=1, padx=10, pady=5)
        start_entry.bind('<KeyRelease>', self.on_start_time_change)
        
        # End time input
        end_label = ctk.CTkLabel(time_frame, text="End Time (HH:MM:SS):")
        end_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.end_time_var = tk.StringVar(value="00:00:00")
        end_entry = ctk.CTkEntry(time_frame, textvariable=self.end_time_var, width=100)
        end_entry.grid(row=0, column=3, padx=10, pady=5)
        end_entry.bind('<KeyRelease>', self.on_end_time_change)
        
        # Configure grid weights for time_frame
        time_frame.grid_columnconfigure(1, weight=1)
        time_frame.grid_columnconfigure(3, weight=1)
        
        # Action buttons frame (right side)
        action_frame = ctk.CTkFrame(trim_frame)
        action_frame.pack(fill="x", pady=(20, 0))
        
        # Preview trim button
        preview_button = ctk.CTkButton(
            action_frame,
            text="Preview Trim",
            command=self.preview_trim,
            width=150
        )
        preview_button.pack(pady=10)
        
        # Trim and save button
        trim_button = ctk.CTkButton(
            action_frame,
            text="Trim & Save Video",
            command=self.trim_and_save,
            width=150
        )
        trim_button.pack(pady=10)
        
    def open_video_file(self):
        """Open video file dialog and load the selected video"""
        file_types = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=file_types
        )
        
        if file_path:
            self.load_video(file_path)
            
    def load_video(self, file_path):
        """Load the selected video file"""
        try:
            self.video_path = file_path
            self.file_label.configure(text=f"Loaded: {os.path.basename(file_path)}")
            
            # Load video with OpenCV for preview
            self.cap = cv2.VideoCapture(file_path)
            if not self.cap.isOpened():
                raise Exception("Could not open video file")
                
            # Get video properties
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.video_duration = self.total_frames / self.fps
            
            # Get comprehensive video info using VideoProcessor
            self.video_info = self.video_processor.get_video_info(file_path)
            
            # Create temp directory for thumbnails
            self.temp_dir = tempfile.mkdtemp(prefix="trimmothy_")
            
                        # Update UI elements
            self.progress_slider.configure(to=self.total_frames-1)
            self.start_trim_slider.configure(to=self.video_duration)
            self.end_trim_slider.configure(to=self.video_duration)
            
            # Set sensible default trim values (10% to 90% of video)
            default_start = min(self.video_duration * 0.1, 10.0)  # 10% or 10 seconds, whichever is smaller
            default_end = max(self.video_duration * 0.9, self.video_duration - 10.0)  # 90% or last 10 seconds, whichever is larger
            
            # Ensure we have at least 1 second of content
            if default_end - default_start < 1.0:
                default_start = 0
                default_end = min(self.video_duration, 30.0)  # First 30 seconds or full video if shorter
            
            self.start_trim_slider.set(default_start)
            self.end_trim_slider.set(default_end)

            # Update time displays
            self.start_time_var.set(self.seconds_to_time_string(default_start))
            self.end_time_var.set(self.seconds_to_time_string(default_end))
            self.trim_start = default_start
            self.trim_end = default_end
            
            # Update video time displays
            if self.start_time_display:
                self.start_time_display.configure(text="00:00:00")
            if self.end_time_display:
                self.end_time_display.configure(text=self.seconds_to_time_string(self.video_duration))
            if self.current_time_label:
                self.current_time_label.configure(text="00:00:00")
            
            # Update trim info label
            self.update_trim_info_label()
            
            # Display first frame
            self.display_frame(0)
            
            # Generate and display thumbnails
            self.generate_thumbnails()
            self.display_thumbnails()
            
            messagebox.showinfo("Success", "Video loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
            
    def display_frame(self, frame_number):
        """Display a specific frame in the video preview"""
        if self.cap is None:
            return
            
        try:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame to fit in the preview area
                height, width = frame.shape[:2]
                max_width, max_height = 600, 400
                
                if width > max_width or height > max_height:
                    scale = min(max_width/width, max_height/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert to PIL Image and then to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                # Update the video label
                self.video_label.configure(image=photo, text="")
                self.video_label.image = photo  # Keep a reference
                
        except Exception as e:
            print(f"Error displaying frame: {e}")
            
    def on_progress_change(self, value):
        """Handle progress slider change"""
        if self.cap is not None:
            # Stop playback when user manually moves slider
            if self.is_playing:
                self.pause_video()
                
            frame_number = int(float(value))
            self.current_frame = frame_number
            self.display_frame(frame_number)
            
            # Update current time display
            current_time = frame_number / self.fps if self.fps > 0 else 0
            if self.current_time_label:
                self.current_time_label.configure(text=self.seconds_to_time_string(current_time))
            
    def toggle_playback(self):
        """Toggle video playback"""
        if self.cap is None:
            messagebox.showwarning("Warning", "Please load a video file first")
            return
            
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()
            
    def play_video(self):
        """Start video playback"""
        if self.cap is None:
            return
            
        self.is_playing = True
        self.play_button.configure(text="⏸ Pause")
        self.playback_frame()
        
    def pause_video(self):
        """Pause video playback"""
        self.is_playing = False
        self.play_button.configure(text="▶ Play")
        if self.playback_timer:
            self.root.after_cancel(self.playback_timer)
            self.playback_timer = None
            
    def playback_frame(self):
        """Play next frame"""
        if not self.is_playing or self.cap is None:
            return
            
        # Advance to next frame
        self.current_frame += 1
        
        # Check if we've reached the end (normal or preview mode)
        reached_end = False
        if self._preview_mode and self.current_frame >= self._preview_end_frame:
            # Preview mode: stop at trim end
            reached_end = True
            self._preview_mode = False
        elif self.current_frame >= self.total_frames:
            # Normal mode: stop at video end
            reached_end = True
            
        if reached_end:
            self.pause_video()
            if not self._preview_mode:  # Only reset to beginning in normal mode
                self.current_frame = 0
                self.progress_slider.set(0)
            return
            
        # Display the frame
        self.display_frame(self.current_frame)
        self.progress_slider.set(self.current_frame)
        
        # Update current time display
        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        if self.current_time_label:
            self.current_time_label.configure(text=self.seconds_to_time_string(current_time))
        
        # Schedule next frame
        delay = int(1000 / self.playback_speed)  # Convert to milliseconds
        self.playback_timer = self.root.after(delay, self.playback_frame)
            
    def on_start_trim_change(self, value):
        """Handle start trim slider change"""
        if self.video_duration > 0:
            self.trim_start = float(value)
            # Ensure start doesn't exceed end
            if self.trim_start >= self.trim_end:
                self.trim_start = max(0, self.trim_end - 1)
                self.start_trim_slider.set(self.trim_start)
            
            # Update time input
            self.start_time_var.set(self.seconds_to_time_string(self.trim_start))
            self.update_trim_info_label()
            
    def on_end_trim_change(self, value):
        """Handle end trim slider change"""
        if self.video_duration > 0:
            self.trim_end = float(value)
            # Ensure end doesn't go below start
            if self.trim_end <= self.trim_start:
                self.trim_end = min(self.video_duration, self.trim_start + 1)
                self.end_trim_slider.set(self.trim_end)
            
            # Update time input
            self.end_time_var.set(self.seconds_to_time_string(self.trim_end))
            self.update_trim_info_label()
            
    def update_trim_info_label(self):
        """Update the trim information label"""
        if self.video_duration > 0:
            duration = self.trim_end - self.trim_start
            start_str = self.seconds_to_time_string(self.trim_start)
            end_str = self.seconds_to_time_string(self.trim_end)
            duration_str = self.seconds_to_time_string(duration)
            
            info_text = f"Trim: {start_str} - {end_str} (Duration: {duration_str})"
            self.trim_info_label.configure(text=info_text)
        
    def on_start_time_change(self, event):
        """Handle start time input change"""
        try:
            time_str = self.start_time_var.get()
            seconds = self.time_string_to_seconds(time_str)
            if 0 <= seconds <= self.video_duration and seconds < self.trim_end:
                self.trim_start = seconds
                self.start_trim_slider.set(seconds)
                self.update_trim_info_label()
        except:
            pass  # Invalid time format, ignore
            
    def on_end_time_change(self, event):
        """Handle end time input change"""
        try:
            time_str = self.end_time_var.get()
            seconds = self.time_string_to_seconds(time_str)
            if 0 <= seconds <= self.video_duration and seconds > self.trim_start:
                self.trim_end = seconds
                self.end_trim_slider.set(seconds)
                self.update_trim_info_label()
        except:
            pass  # Invalid time format, ignore
            
    def time_string_to_seconds(self, time_str):
        """Convert HH:MM:SS string to seconds"""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                # Validate values
                if 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59:
                    return hours * 3600 + minutes * 60 + seconds
            return 0
        except (ValueError, AttributeError):
            return 0
        
    def seconds_to_time_string(self, seconds):
        """Convert seconds to HH:MM:SS string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def generate_thumbnails(self):
        """Generate thumbnail images for the video timeline"""
        if self.cap is None or self.total_frames == 0:
            return
            
        self.thumbnail_images = []
        
        # Calculate frame intervals for thumbnails
        interval = max(1, self.total_frames // self.thumbnail_count)
        
        for i in range(self.thumbnail_count):
            frame_number = min(i * interval, self.total_frames - 1)
            
            # Set frame position
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            
            if ret:
                # Convert from BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize to thumbnail size (maintaining aspect ratio)
                height, width = frame.shape[:2]
                thumb_width = 120
                thumb_height = int((thumb_width * height) / width)
                thumb_height = min(thumb_height, 80)  # Max height limit
                
                frame = cv2.resize(frame, (thumb_width, thumb_height))
                
                # Convert to PIL Image and then to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                self.thumbnail_images.append(photo)
            else:
                # Add placeholder if frame can't be read
                self.thumbnail_images.append(None)
    
    def display_thumbnails(self):
        """Display thumbnails in the thumbnail frame"""
        if not self.thumbnail_images or self.thumbnail_frame is None:
            return
            
        # Clear existing thumbnails
        for label in self.thumbnail_labels:
            label.destroy()
        self.thumbnail_labels = []
        
        # Create thumbnail labels
        for i, thumb_image in enumerate(self.thumbnail_images):
            if thumb_image:
                # Calculate timestamp for this thumbnail
                interval = max(1, self.total_frames // self.thumbnail_count)
                frame_number = min(i * interval, self.total_frames - 1)
                timestamp = self.seconds_to_time_string(frame_number / self.fps)
                
                # Create container for thumbnail and timestamp
                thumb_container = ctk.CTkFrame(self.thumbnail_frame)
                thumb_container.pack(side="left", padx=2, pady=5)
                
                # Thumbnail image
                label = ctk.CTkLabel(
                    thumb_container,
                    image=thumb_image,
                    text="",
                    width=120,
                    height=80,
                    cursor="hand2"
                )
                label.pack()
                
                # Timestamp below thumbnail
                time_label = ctk.CTkLabel(
                    thumb_container,
                    text=timestamp,
                    font=ctk.CTkFont(size=10)
                )
                time_label.pack()
                
                self.thumbnail_labels.append(thumb_container)
                
                # Add click binding for seeking (bind to both thumbnail and container)
                label.bind("<Button-1>", lambda e, idx=i: self.seek_to_thumbnail(idx))
                thumb_container.bind("<Button-1>", lambda e, idx=i: self.seek_to_thumbnail(idx))
    
    def seek_to_thumbnail(self, thumbnail_index):
        """Seek to the position represented by a thumbnail"""
        if self.total_frames == 0:
            return
            
        # Calculate frame position
        interval = max(1, self.total_frames // self.thumbnail_count)
        target_frame = min(thumbnail_index * interval, self.total_frames - 1)
        
        # Update current frame and display
        self.current_frame = target_frame
        self.progress_slider.set(target_frame)
        self.display_frame(target_frame)
        
        # Update time displays
        current_time = target_frame / self.fps
        if self.current_time_label:
            self.current_time_label.configure(text=self.seconds_to_time_string(current_time))
        
    def preview_trim(self):
        """Preview the selected trim by playing the trimmed section"""
        if self.video_path is None:
            messagebox.showwarning("Warning", "Please load a video file first")
            return
            
        if self.trim_start >= self.trim_end:
            messagebox.showwarning("Warning", "Invalid trim selection")
            return
            
        try:
            # Stop any current playback
            if self.is_playing:
                self.pause_video()
            
            # Jump to start of trim
            start_frame = int(self.trim_start * self.fps)
            self.current_frame = start_frame
            self.progress_slider.set(start_frame)
            self.display_frame(start_frame)
            
            # Update current time display
            if self.current_time_label:
                self.current_time_label.configure(text=self.seconds_to_time_string(self.trim_start))
            
            # Start playback (it will automatically stop at end during normal playback)
            self.play_video()
            
            # Set a flag to stop at trim end
            self._preview_mode = True
            self._preview_end_frame = int(self.trim_end * self.fps)
            
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed: {str(e)}")
            
    def trim_and_save(self):
        """Trim the video and save it"""
        if self.video_path is None:
            messagebox.showwarning("Warning", "Please load a video file first")
            return
            
        if self.trim_start >= self.trim_end:
            messagebox.showwarning("Warning", "Invalid trim selection. Start time must be before end time.")
            return
            
        if self.trim_end - self.trim_start < 0.1:
            messagebox.showwarning("Warning", "Trim duration too short. Please select at least 0.1 seconds.")
            return
            
        if self.trim_start < 0 or self.trim_end > self.video_duration:
            messagebox.showwarning("Warning", "Trim selection is outside video bounds.")
            return
            
        # Ask user where to save the file
        original_name = Path(self.video_path).stem
        original_ext = Path(self.video_path).suffix
        default_name = f"{original_name}--trimmothy{original_ext}"
        
        save_path = filedialog.asksaveasfilename(
            title="Save trimmed video as",
            defaultextension=original_ext,
            initialfile=default_name,
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )
        
        if save_path:
            self.perform_trim(save_path)
            
    def perform_trim(self, output_path):
        """Perform the actual video trimming"""
        try:
            # Show progress dialog
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Trimming Video")
            progress_window.geometry("450x200")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ctk.CTkLabel(progress_window, text="Trimming video, please wait...")
            progress_label.pack(pady=20)
            
            progress_bar = ctk.CTkProgressBar(progress_window)
            progress_bar.pack(padx=20, pady=10, fill="x")
            progress_bar.set(0)
            
            # Add cancel functionality
            cancel_requested = {"value": False}
            
            def cancel_encoding():
                cancel_requested["value"] = True
                progress_label.configure(text="Cancelling... Please wait")
                cancel_button.configure(state="disabled")
            
            cancel_button = ctk.CTkButton(
                progress_window, 
                text="Cancel", 
                command=cancel_encoding,
                fg_color="red",
                hover_color="darkred"
            )
            cancel_button.pack(pady=10)
            
            def trim_video():
                try:
                    if cancel_requested["value"]:
                        return
                    
                    # Update progress callback
                    def progress_callback(progress):
                        if not cancel_requested["value"]:
                            progress_bar.set(progress)
                            progress_window.update()
                        
                    # Check if output directory exists
                    if not ensure_directory_exists(output_path):
                        raise Exception(f"Cannot create output directory")
                    
                    # Use VideoProcessor for fast and reliable trimming
                    progress_label.configure(text="Processing video with FFmpeg...")
                    progress_window.update()
                    
                    success = self.video_processor.trim_video(
                        self.video_path,
                        output_path,
                        self.trim_start,
                        self.trim_end,
                        progress_callback=progress_callback
                    )
                    
                    if cancel_requested["value"]:
                        return
                    
                    if success:
                        # Update progress
                        progress_bar.set(1.0)
                        progress_label.configure(text="Complete!")
                        progress_window.update()
                        
                        # Small delay to show completion
                        progress_window.after(500, progress_window.destroy)
                        
                        # Show success message
                        duration = seconds_to_time_string(self.trim_end - self.trim_start)
                        self.root.after(600, lambda: messagebox.showinfo("Success", 
                            f"Video trimmed and saved successfully!\n\nLocation: {output_path}\n"
                            f"Duration: {duration}"))
                    else:
                        raise Exception("Video processing failed")
                    
                except PermissionError:
                    if progress_window.winfo_exists():
                        progress_window.destroy()
                    messagebox.showerror("Permission Error", 
                        "Cannot write to the selected location. Please choose a different location or check file permissions.")
                except FileNotFoundError:
                    if progress_window.winfo_exists():
                        progress_window.destroy()
                    messagebox.showerror("File Error", 
                        "Output directory not found. Please select a valid location.")
                except Exception as e:
                    if progress_window.winfo_exists():
                        progress_window.destroy()
                    error_msg = str(e)
                    if "ffmpeg" in error_msg.lower():
                        messagebox.showerror("FFmpeg Error", 
                            "Video processing failed. Please ensure FFmpeg is properly installed.")
                    elif "codec" in error_msg.lower():
                        messagebox.showerror("Codec Error", 
                            "Video encoding failed. This might be due to an unsupported video format or codec issue.")
                    elif "memory" in error_msg.lower():
                        messagebox.showerror("Memory Error", 
                            "Not enough memory to process this video. Try trimming a shorter segment.")
                    else:
                        messagebox.showerror("Error", f"Failed to trim video: {error_msg}")
                finally:
                    # Handle cancellation
                    if cancel_requested["value"]:
                        if progress_window.winfo_exists():
                            progress_window.destroy()
                        # Clean up partial file if it exists
                        cleanup_temp_files(output_path)
            
            # Run trimming in a separate thread
            threading.Thread(target=trim_video, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start trimming: {str(e)}")
            
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        finally:
            # Cleanup
            self.is_playing = False  # Stop any ongoing playback
            if self.cap:
                self.cap.release()
            if self.temp_dir:
                cleanup_temp_files(self.temp_dir)

def main():
    """Main entry point"""
    app = TrimmothyApp()
    app.run()

if __name__ == "__main__":
    main() 