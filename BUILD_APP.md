# Building Trimmothy as a macOS App

This guide explains how to package Trimmothy as a standalone macOS application.

## Quick Start

1. **Build the app:**
   ```bash
   ./build_macos_app.sh
   ```

2. **Test the app:**
   ```bash
   open dist/Trimmothy.app
   ```

## Prerequisites

- **Poetry**: The app uses Poetry for dependency management
- **Python 3.13**: Required for the application
- **FFmpeg**: Required for video processing (installed via `brew install ffmpeg`)
  - **Note**: FFmpeg binaries will be automatically bundled with your app!

## Build Process

The build script (`build_macos_app.sh`) will:

1. ✅ Check that Poetry is installed
2. ✅ Install PyInstaller if not already present
3. ✅ Check for FFmpeg availability
4. 🧹 Clean previous builds
5. 🚀 Build the macOS app using PyInstaller

## Output

After building, you'll find:
- `dist/Trimmothy.app` - The standalone macOS application
- `build/` - Temporary build files (can be deleted)

## Distribution

### For Personal Use
- Simply copy `Trimmothy.app` to your Applications folder
- ✅ **No additional setup required** - FFmpeg is bundled!

### For Others
1. **Zip the app**: Create a ZIP file containing `Trimmothy.app`
2. **✅ FFmpeg included**: No additional software installation required
3. **Consider code signing**: For wider distribution without security warnings

## Adding an App Icon (Optional)

To add a custom icon:

1. Create or find a 1024x1024 PNG icon
2. Convert to ICNS format:
   ```bash
   mkdir icon.iconset
   sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
   sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
   sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
   sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
   sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
   sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
   sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
   sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
   sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
   sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
   iconutil -c icns icon.iconset
   rm -rf icon.iconset
   ```
3. Place the resulting `icon.icns` file in the project root
4. Rebuild the app

## Code Signing (For Distribution)

To distribute without security warnings:

1. **Get a Developer ID**: Requires an Apple Developer account ($99/year)
2. **Sign the app**:
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/Trimmothy.app
   ```
3. **Notarize with Apple**: Required for macOS 10.15+

## Troubleshooting

### "App is damaged" message
- This happens with unsigned apps
- Right-click → Open, then click "Open" in the dialog
- Or use: `xattr -cr dist/Trimmothy.app`

### FFmpeg not found
- Install FFmpeg: `brew install ffmpeg`
- Ensure it's in the PATH

### Build fails
- Check that Poetry and Python 3.13 are properly installed
- Try cleaning: `rm -rf build/ dist/ *.spec`
- Run the build script again

## Advanced: Universal Binary

The build script creates a universal binary that works on both Intel and Apple Silicon Macs automatically. 