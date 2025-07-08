#!/bin/bash

# Trimmothy Video Trimmer - Poetry Launcher
# Quick launcher for Poetry users

echo "🎬 Trimmothy Video Trimmer (Poetry)"
echo "===================================="

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed."
    echo "   Install it with: curl -sSL https://install.python-poetry.org | python3 -"
    echo "   Or use the alternative installer: ./install_and_run.sh"
    exit 1
fi

# Check if tkinter is available
echo "🔍 Checking tkinter support..."
if ! poetry run python -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter is not available."
    echo ""
    echo "Fix this with:"
    echo "  brew install python-tk"
    echo "  poetry env remove \$(poetry env list | head -n1 | cut -d' ' -f1)"
    echo "  poetry install"
    echo ""
    exit 1
else
    echo "✅ tkinter is available"
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! poetry run python -c "import customtkinter, moviepy, cv2, PIL, numpy" 2>/dev/null; then
    echo "⚠️  Installing missing dependencies..."
    poetry install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✅ All dependencies are ready"
echo ""
echo "🚀 Starting Trimmothy Video Trimmer..."
echo "   (GUI should open in a moment)"
echo ""

# Run the application
poetry run trimmothy

echo ""
echo "👋 Thanks for using Trimmothy!" 