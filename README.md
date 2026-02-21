# AI Vision Detector

A real-time object detection desktop application powered by YOLOv8 and PyQt5.

[![GitHub Stars](https://img.shields.io/github/stars/Ranaweerakgls/AI-Vision-Detector)](https://github.com/Ranaweerakgls/AI-Vision-Detector/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Ranaweerakgls/AI-Vision-Detector)](https://github.com/Ranaweerakgls/AI-Vision-Detector/issues)

## Overview

AI Vision Detector is a modern desktop application that provides real-time object detection using state-of-the-art YOLOv8 neural network. Built with PyQt5, it offers a sleek dark-themed interface with comprehensive controls for detection parameters, video source selection, and recording capabilities.

## Features

- **Real-time Object Detection** - Detect objects in real-time using YOLOv8 nano model
- **Multiple Video Sources** - Use webcam or load any video file (MP4, AVI, MOV)
- **Adjustable Confidence Threshold** - Fine-tune detection sensitivity (1-100%)
- **Custom Inference Resolution** - Adjust resolution from 320px to 1280px
- **GPU Acceleration** - Option to use CUDA GPU for faster processing (if available)
- **Screenshot Capture** - Save current frame as PNG image
- **Video Recording** - Record detection sessions to AVI format
- **Live Statistics** - View FPS, object count, and total detections
- **Collapsible Panels** - Organize UI with expandable/collapsible sections
- **Dark Theme UI** - Modern dark-themed interface with color-coded detections

## Requirements

- Python 3.8+
- Windows, macOS, or Linux

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ranaweerakgls/AI-Vision-Detector.git
cd AI-Vision-Detector
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the YOLOv8 model (automatically downloaded on first run):
   - The app uses `yolov8n.pt` (nano model) which is ~6MB
   - Model is automatically downloaded by ultralytics on first use

## Usage

1. Run the application:
```bash
python main.py
```

2. **Starting Detection**:
   - Select video source (Webcam or Video File)
   - Adjust confidence threshold and resolution as needed
   - Click "Start Detection" button

3. **Controls**:
   - **Source**: Choose webcam (default) or select a video file
   - **Device**: Select CPU or GPU (if CUDA available)
   - **Confidence**: Adjust detection confidence (default 25%)
   - **Resolution**: Set inference resolution (default 640px)

4. **Recording**:
   - Click "Record" to start recording
   - Click "Stop Recording" to save the video as `output.avi`

5. **Screenshots**:
   - Click "Screenshot" to save current frame as PNG

## Project Structure

```
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
├── yolov8n.pt          # YOLOv8 nano model weights
├── assets/
│   └── logo.png        # Application logo
└── screenshot.png      # Saved screenshots (generated)
```

## Dependencies

- **ultralytics** - YOLOv8 framework
- **opencv-python** - Video/image processing
- **torch** - PyTorch backend
- **torchvision** - Torch vision utilities
- **PyQt5** - GUI framework

## Technical Details

- **Model**: YOLOv8n (nano) - fastest and smallest model
- **Default Resolution**: 640px
- **Default Confidence**: 25%
- **Video Output**: AVI format (XVID codec)
- **Screenshot Format**: PNG

