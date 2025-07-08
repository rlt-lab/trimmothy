#!/bin/bash

# Build script for Trimmothy macOS app
echo "🎬 Trimmothy macOS App Builder"
echo "============================="

# Check if we're in a poetry environment
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# Check if PyInstaller is available
echo "🔍 Checking PyInstaller..."
if ! poetry run python -c "import PyInstaller" 2>/dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    poetry add --group dev pyinstaller
fi

# Check if FFmpeg is available and copy binaries for bundling
echo "🔍 Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found!"
    echo "   The app will require FFmpeg to be installed on the target machine."
    echo "   Users can install it with: brew install ffmpeg"
    echo "   Continuing build anyway..."
else
    echo "✅ FFmpeg found"
    
    # Copy FFmpeg binaries for bundling if they don't exist
    if [ ! -f "resources/bin/ffmpeg" ] || [ ! -f "resources/bin/ffprobe" ]; then
        echo "📦 Copying FFmpeg binaries for bundling..."
        mkdir -p resources/bin
        cp "$(which ffmpeg)" resources/bin/
        cp "$(which ffprobe)" resources/bin/
        echo "✅ FFmpeg binaries copied to resources/bin/"
    else
        echo "✅ FFmpeg binaries already available for bundling"
    fi
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Build the app
echo "🚀 Building macOS app..."
poetry run python build_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Build completed successfully!"
    echo "📱 Your app is located at: dist/Trimmothy.app"
    echo ""
    echo "🎯 To test your app:"
    echo "   open dist/Trimmothy.app"
    echo ""
    echo "📋 To distribute your app:"
    echo "   1. Zip the Trimmothy.app folder"
    if [ -f "resources/bin/ffmpeg" ]; then
        echo "   2. ✅ FFmpeg is bundled - no additional installation required!"
    else
        echo "   2. ⚠️  Users will need FFmpeg installed (brew install ffmpeg)"
    fi
    echo "   3. Consider code signing for distribution outside the App Store"
else
    echo "❌ Build failed!"
    exit 1
fi 