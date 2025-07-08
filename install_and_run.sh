#!/bin/bash

# Trimmothy Video Trimmer - Installation and Launch Script
# For macOS users

echo "🎬 Trimmothy Video Trimmer Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "   Please install Python 3.13+ with tkinter support:"
    echo "   1. Download from: https://www.python.org/downloads/"
    echo "   2. Or use Homebrew: brew install python-tk"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Found Python $python_version"

# Check if tkinter is available
echo "🔍 Checking tkinter support..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter is not available with your Python installation."
    echo ""
    echo "To fix this on macOS:"
    echo "1. If you installed Python via Homebrew:"
    echo "   brew install python-tk"
    echo ""
    echo "2. Or install Python from python.org which includes tkinter:"
    echo "   https://www.python.org/downloads/"
    echo ""
    echo "3. Or install tkinter specifically:"
    echo "   On macOS with Homebrew: brew install tcl-tk"
    echo ""
    exit 1
else
    echo "✅ tkinter is available"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "trimmothy_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv trimmothy_env
else
    echo "📦 Using existing virtual environment..."
fi

# Activate virtual environment
source trimmothy_env/bin/activate

# Install dependencies
echo ""
echo "📦 Installing required dependencies..."
echo "   This may take a few minutes..."

pip install customtkinter moviepy opencv-python pillow numpy

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

# Test import
echo "🧪 Testing application import..."
if python3 -c "import sys; sys.path.insert(0, 'src'); from trimmothy.main import TrimmothyApp" 2>/dev/null; then
    echo "✅ Application modules imported successfully!"
else
    echo "❌ Failed to import application modules."
    echo "   Please check that all dependencies are properly installed."
    exit 1
fi

echo ""
echo "🚀 Starting Trimmothy Video Trimmer..."
echo "   (Make sure you have a video file ready to trim!)"
echo ""

# Run the application
PYTHONPATH=src python3 -m trimmothy.main

echo ""
echo "👋 Thanks for using Trimmothy!" 