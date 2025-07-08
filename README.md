# Trimmothy - Video Trimmer for macOS

A simple and elegant video trimming application built with Python, featuring a modern GUI interface for macOS users.

## Features

- **Easy Video Loading**: Open video files through a simple file dialog
- **Live Video Preview**: See video frames as you navigate through the timeline
- **Video Playback**: Play/pause button for real-time video preview
- **Dual Trim Controls**: 
  - Interactive sliders for visual trim selection
  - Manual time input in HH:MM:SS format
- **Real-time Feedback**: Live preview of trim selection with duration display
- **Smart File Naming**: Automatically appends "--trimmothy" suffix to output files
- **Progress Tracking**: Visual progress bar during video processing
- **Format Support**: Works with most common video formats (MP4, AVI, MOV, MKV, WMV, FLV, WebM)
- **Error Handling**: Comprehensive error messages and validation

## Requirements

- **macOS** (designed specifically for macOS)
- **Python 3.13+** with **tkinter support**
- **Poetry** (for dependency management)

## Installation

### Option 1: Using Poetry (Recommended)

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Ensure Python has tkinter support**:
   ```bash
   # Install Python with tkinter via Homebrew
   brew install python-tk
   ```

3. **Clone this repository**:
   ```bash
   git clone <repository-url>
   cd trimmothy
   ```

4. **Install dependencies**:
   ```bash
   poetry install
   ```

5. **Run the application**:
   ```bash
   poetry run trimmothy
   ```

### Option 2: Poetry Shell

You can also activate Poetry's virtual environment:

```bash
poetry shell                    # Activate Poetry's virtual environment
trimmothy                      # Run the application directly
# or
python -m trimmothy.main       # Alternative way to run
exit                          # Exit the Poetry shell when done
```

### Option 3: Manual Installation (Alternative)

If you prefer not to use Poetry:

1. **Ensure Python with tkinter is installed**:
   ```bash
   brew install python-tk
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv trimmothy_env
   source trimmothy_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install customtkinter moviepy opencv-python pillow numpy
   ```

4. **Run the application**:
   ```bash
   PYTHONPATH=src python3 -m trimmothy.main
   ```

### Option 4: Automatic Installer

```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

## Poetry Workflow

### Managing Dependencies

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree

# Check for security vulnerabilities
poetry show --outdated
```

### Virtual Environment Management

```bash
# Check environment info
poetry env info

# List environments
poetry env list

# Remove environment
poetry env remove <env-name>

# Use specific Python version
poetry env use python3.13
```

### Running Commands

```bash
# Run the application
poetry run trimmothy

# Run Python scripts
poetry run python script.py

# Run any command in the Poetry environment
poetry run <command>

# Open a shell in the Poetry environment
poetry shell
```

## Usage Workflow

### 1. Open a Video File
- Click "Open Video File" button
- Select your video file from the file dialog
- The video will load and display the first frame
- Use the "▶ Play" button to preview your video

### 2. Set Trim Points
You have two ways to set your trim selection:

**Option A: Using Sliders**
- Use the "Start" slider to set the beginning of your trim
- Use the "End" slider to set the end of your trim
- The sliders will automatically prevent invalid selections

**Option B: Manual Time Entry**
- Type start time in the "Start Time (HH:MM:SS)" field
- Type end time in the "End Time (HH:MM:SS)" field
- Format: `HH:MM:SS` (e.g., `00:01:30` for 1 minute 30 seconds)

### 3. Preview Your Selection
- Click "Preview Trim" to see trim details
- The preview will show:
  - Start time
  - End time  
  - Duration of the trimmed segment
- Use the video progress slider to scrub through and verify your selection

### 4. Save Trimmed Video
- Click "Trim & Save Video"
- Choose where to save your trimmed video
- The default filename will include "--trimmothy" suffix
- Wait for processing to complete
- Your trimmed video will be saved with high quality (H.264/AAC)

## Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│                 Trimmothy Video Trimmer                 │
├─────────────────────────────────────────────────────────┤
│ [No video file selected]              [Open Video File] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                 Video Preview Area                      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ [▶ Play]                                               │
│ Video Progress: [====================|]                 │
│                                                         │
│ Trim Selection: 00:01:30 - 00:03:45 (Duration: 00:02:15)│
│ Start: [=====|          ] End: [========|    ]          │
│                                                         │
│ Start Time (HH:MM:SS): [00:01:30]                      │
│ End Time (HH:MM:SS):   [00:03:45]                      │
├─────────────────────────────────────────────────────────┤
│ [Preview Trim]                    [Trim & Save Video]   │
└─────────────────────────────────────────────────────────┘
```

## Tips & Best Practices

1. **File Formats**: MP4 files generally work best for both input and output
2. **File Naming**: The "--trimmothy" suffix helps you identify trimmed videos
3. **Precision**: Use manual time entry for precise trim points
4. **Preview**: Use the play button to preview your video and the "Preview Trim" to verify your selection
5. **Playback**: The play button will automatically pause when you manually move the progress slider
6. **File Size**: Longer videos may take more time to process
7. **Quality**: Output videos maintain high quality using H.264 encoding

## Troubleshooting

### Common Issues

**"No module named '_tkinter'"**
- Your Python installation doesn't include tkinter
- **Solution**: `brew install python-tk` then recreate Poetry environment:
  ```bash
  poetry env remove $(poetry env list | grep Activated | cut -d' ' -f1)
  poetry install
  ```

**"Could not open video file"**
- Check if the video file is corrupted
- Try a different video format
- Ensure the file path doesn't contain special characters

**"Permission Error"**
- Choose a different save location
- Check if you have write permissions to the selected folder
- Try saving to your Desktop or Documents folder

**"Codec Error"**
- Try with a different input video format
- Ensure your video isn't corrupted
- Some very old or proprietary formats may not be supported

**"Memory Error"**
- Try trimming a shorter segment
- Close other applications to free up memory
- For very large videos, consider trimming in smaller segments

**Poetry Environment Issues**
- Remove and recreate environment: `poetry env remove <env-name> && poetry install`
- Check Poetry configuration: `poetry config --list`
- Update Poetry: `poetry self update`

## Development

### Project Structure

```
trimmothy/
├── src/trimmothy/           # Source code
│   ├── __init__.py
│   └── main.py             # Main application
├── pyproject.toml          # Poetry configuration
├── README.md               # This file
├── run_trimmothy.py        # Alternative launcher
└── install_and_run.sh      # Shell installer
```

### Adding Features

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `poetry install --with dev`
4. Make your changes
5. Test: `poetry run trimmothy`
6. Submit a pull request

## Technical Details

- **Video Processing**: Uses MoviePy for high-quality video processing
- **Preview**: OpenCV for fast frame extraction and display
- **GUI**: CustomTkinter for modern, native-looking interface
- **Threading**: Video processing runs in background threads to keep UI responsive
- **Output Quality**: H.264 video codec with AAC audio codec for best compatibility
- **Dependency Management**: Poetry for reproducible installations

## Quick Start

```bash
# With Poetry (recommended)
poetry install && poetry run trimmothy

# Without Poetry
./install_and_run.sh
```

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve Trimmothy!
