#!/usr/bin/env python3
"""
Launcher script for Trimmothy Video Trimmer

This script launches the Trimmothy video trimming application.

Usage:
    python run_trimmothy.py
"""

import sys
import os
from pathlib import Path

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def check_virtual_env():
    """Check if we're in a virtual environment with dependencies"""
    try:
        import customtkinter
        import moviepy
        import cv2
        import PIL
        import numpy
        return True
    except ImportError:
        return False

def main():
    print("🎬 Trimmothy Video Trimmer")
    print("=" * 30)
    
    # Check tkinter first
    if not check_tkinter():
        print("❌ tkinter is not available with your Python installation.")
        print("\nTo fix this on macOS:")
        print("1. Install Python from python.org (includes tkinter)")
        print("2. Or use: brew install python-tk")
        print("3. Or run the installer: ./install_and_run.sh")
        return 1
    
    # Check if we have dependencies
    if not check_virtual_env():
        print("⚠️  Dependencies not found in current environment.")
        print("\nOptions to fix this:")
        print("1. Run the installer: ./install_and_run.sh")
        print("2. Activate virtual environment: source trimmothy_env/bin/activate")
        print("3. Install manually: pip install customtkinter moviepy opencv-python pillow numpy")
        return 1
    
    # Add the src directory to the Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from trimmothy.main import main
        
        print("✅ Starting Trimmothy Video Trimmer...")
        print("   Make sure you have a video file ready to trim!")
        print()
        
        main()
        
    except ImportError as e:
        print(f"❌ Error importing Trimmothy: {e}")
        print("\nPlease run the installer: ./install_and_run.sh")
        return 1
    except Exception as e:
        print(f"❌ Error starting Trimmothy: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code) 