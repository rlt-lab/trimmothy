#!/usr/bin/env python3
"""
Build script for creating Trimmothy macOS app using PyInstaller
"""

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_app():
    """Build the macOS app using PyInstaller"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define paths
    main_script = current_dir / "src" / "trimmothy" / "main.py"
    icon_path = current_dir / "icon.icns"  # We'll create this if needed
    resources_dir = current_dir / "resources"
    
    # PyInstaller arguments
    args = [
        str(main_script),
        "--name=Trimmothy",
        "--windowed",  # Don't show console window
        "--onedir",    # Create a directory bundle
        "--clean",     # Clean PyInstaller cache
        f"--distpath={current_dir / 'dist'}",
        f"--workpath={current_dir / 'build'}",
        f"--specpath={current_dir}",
        # Include necessary data files and modules
        "--hidden-import=customtkinter",
        "--hidden-import=PIL._tkinter_finder",
        "--collect-all=customtkinter",
        "--collect-all=PIL",
        # Include FFmpeg binaries
        f"--add-binary={resources_dir / 'bin' / 'ffmpeg'}:.",
        f"--add-binary={resources_dir / 'bin' / 'ffprobe'}:.",
        # macOS specific options
        "--osx-bundle-identifier=com.trimmothy.videoeditor",
    ]
    
    # Add icon if it exists
    if icon_path.exists():
        args.append(f"--icon={icon_path}")
    
    # Check if FFmpeg binaries exist
    ffmpeg_bin = resources_dir / 'bin' / 'ffmpeg'
    ffprobe_bin = resources_dir / 'bin' / 'ffprobe'
    
    if not ffmpeg_bin.exists() or not ffprobe_bin.exists():
        print("⚠️  FFmpeg binaries not found in resources/bin/")
        print("   Run this to copy them:")
        print("   cp /opt/homebrew/bin/ffmpeg resources/bin/")
        print("   cp /opt/homebrew/bin/ffprobe resources/bin/")
        print("   Or install FFmpeg: brew install ffmpeg")
        print("   Building without bundled FFmpeg (users will need to install it)")
        # Remove the FFmpeg binary args if they don't exist
        args = [arg for arg in args if not arg.startswith('--add-binary=') or 'ffmpeg' not in arg]
    else:
        print("✅ Found bundled FFmpeg binaries")
    
    print("🚀 Building Trimmothy macOS app...")
    print(f"📁 Main script: {main_script}")
    print(f"📦 Output directory: {current_dir / 'dist'}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("✅ Build complete!")
    print(f"📱 Your app is located at: {current_dir / 'dist' / 'Trimmothy.app'}")
    print("\n🎯 To run your app:")
    print(f"   open '{current_dir / 'dist' / 'Trimmothy.app'}'")
    
if __name__ == "__main__":
    build_app() 