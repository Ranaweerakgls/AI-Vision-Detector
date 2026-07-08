# 🤖 AI Vision Detector

> A real-time AI-powered object detection desktop application built with **YOLOv8, PyTorch, OpenCV, and PyQt5**.

[![GitHub Stars](https://img.shields.io/github/stars/Ranaweerakgls/AI-Vision-Detector?style=for-the-badge)](https://github.com/Ranaweerakgls/AI-Vision-Detector/stargazers)

[![GitHub Issues](https://img.shields.io/github/issues/Ranaweerakgls/AI-Vision-Detector?style=for-the-badge)](https://github.com/Ranaweerakgls/AI-Vision-Detector/issues)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-111F68?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-Framework-EE4C2C?style=for-the-badge&logo=pytorch)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv)
![PyQt5](https://img.shields.io/badge/PyQt5-Desktop_GUI-41CD52?style=for-the-badge)

---

# 📖 Overview

**AI Vision Detector** is a modern desktop-based computer vision application that performs **real-time object detection** using the state-of-the-art **YOLOv8 neural network model**.

The application provides a user-friendly graphical interface built with **PyQt5**, allowing users to detect objects from live webcam feeds or uploaded video files while controlling detection parameters such as confidence level, inference resolution, and processing device.

Designed with practical AI deployment in mind, the system demonstrates the integration of deep learning models with real-time video processing and desktop application development.

---

# 🎯 Project Objectives

The main goals of AI Vision Detector are:

- 🤖 Implement real-time object detection using YOLOv8
- 🎥 Process live camera and video inputs
- ⚡ Enable GPU acceleration for faster inference
- 🖥️ Provide an intuitive desktop user interface
- 📊 Display real-time detection analytics
- 🎛️ Allow customizable detection parameters
- 📹 Support detection recording and screenshot capture
- 🧠 Demonstrate practical AI computer vision deployment

---

# ✨ Key Features

## 🎯 Real-Time Object Detection

Powered by the **YOLOv8 Nano model**, the application can detect multiple objects instantly from video streams.

Features:

- ⚡ Real-time inference
- 🎯 Multi-object detection
- 🏷️ Object labels
- 📊 Confidence scores
- 🟦 Bounding box visualization

---

## 🎥 Multiple Video Sources

Supports different input sources:

- 📷 Live Webcam Detection
- 🎞️ Video File Processing

Supported formats:

- MP4
- AVI
- MOV

---

## 🎚️ Adjustable Detection Parameters

Users can customize AI inference settings.

Available controls:

- 🎯 Confidence Threshold (1% - 100%)
- 📐 Inference Resolution (320px - 1280px)
- ⚙️ Processing Device Selection

---

## 🚀 GPU Acceleration

Supports CUDA-based GPU processing when available.

Benefits:

- Faster inference speed
- Improved real-time performance
- Efficient AI model execution

Available options:

- 🖥️ CPU Processing
- ⚡ CUDA GPU Processing

---

## 📸 Screenshot Capture

Capture detected frames instantly.

Features:

- Save current detection frame
- PNG image output
- Automatic screenshot generation

---

## 🎥 Detection Recording

Record AI detection sessions.

Features:

- Start / Stop recording
- Save processed video output
- AVI format support
- XVID codec integration

---

## 📊 Live Detection Statistics

Monitor system performance in real time.

Displays:

- FPS (Frames Per Second)
- Current object count
- Total detections
- Processing information

---

## 🌙 Modern Dark Theme Interface

Built with a clean and modern PyQt5 interface.

UI Features:

- 🌑 Dark-themed design
- 🎨 Color-coded detections
- 📂 Collapsible panels
- 🎛️ Organized controls
- 🖥️ Responsive layout

---

# 🏗️ Application Workflow
Video Source
|
↓
OpenCV Video Capture
|
↓
YOLOv8 Neural Network
|
↓
Object Detection Processing
|
↓
Bounding Box Rendering
|
↓
PyQt5 User Interface Display


---

# 🛠️ Technology Stack

## 🐍 Programming Language

- Python 3.8+

---

## 🤖 Artificial Intelligence

- YOLOv8 Nano Model
- Ultralytics Framework
- PyTorch Deep Learning Framework

---

## 👁️ Computer Vision

- OpenCV
- Real-time video processing
- Image manipulation
- Frame analysis

---

## 🖥️ Desktop Application

- PyQt5
- Custom GUI components
- Event-driven application design

---

# 📦 Dependencies

Main libraries used:

| Library | Purpose |
|---------|---------|
| 🤖 Ultralytics | YOLOv8 object detection framework |
| 👁️ OpenCV | Image and video processing |
| 🔥 PyTorch | Deep learning backend |
| 🖼️ TorchVision | Vision utilities |
| 🖥️ PyQt5 | Desktop GUI development |

---

# ⚙️ Installation

## 1️⃣ Clone Repository

git clone https://github.com/Ranaweerakgls/AI-Vision-Detector.git

cd AI-Vision-Detector
2️⃣ Create Virtual Environment
---

Recommended:

python -m venv venv

Activate environment:
---
Windows
venv\Scripts\activate
macOS/Linux
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ YOLOv8 Model Setup

The application automatically downloads:

yolov8n.pt

Model details:

🧠 Model: YOLOv8 Nano
📦 Size: ~6MB
⚡ Optimized for fast inference
▶️ Usage
---
Run the application:

python main.py
🎮 Application Controls
🎥 Video Source
---
Choose input:

📷 Webcam
🎞️ Video File
⚙️ Detection Settings
---
Customize:

Setting	Description
🎯 Confidence	Detection sensitivity
📐 Resolution	AI inference size
🖥️ Device	CPU / GPU selection
🎬 Recording

Steps:

Click Record
Perform detection
Click Stop Recording
---
Output:

output.avi
📸 Screenshot

Click:

Screenshot

Output:
---

PNG Image File
📂 Project Structure
AI-Vision-Detector/
│
├── main.py                 # Main application
├── requirements.txt        # Dependencies
├── yolov8n.pt             # YOLOv8 model weights
│
├── assets/
│   └── logo.png           # Application logo
│
└── screenshots/
    └── generated images
🔬 Technical Specifications

---
Component	Details
🧠 AI Model	YOLOv8 Nano
⚡ Framework	Ultralytics
🔥 Backend	PyTorch
🎥 Processing	OpenCV
🖥️ Interface	PyQt5
📐 Default Resolution	640px
🎯 Default Confidence	25%
🎞️ Video Output	AVI (XVID Codec)
📸 Image Output	PNG
🚀 Future Improvements
---
Potential enhancements:

🌐 Web-based deployment
📱 Mobile application support
☁️ Cloud AI processing
🧠 Custom trained detection models
📈 Advanced analytics dashboard
🔔 Real-time alerts
👥 Multi-camera monitoring
🎯 Project Outcome
---
AI Vision Detector successfully demonstrates the integration of artificial intelligence, computer vision, and desktop application development into a practical real-time detection system.

The project combines deep learning inference, video processing, GPU acceleration, and an interactive graphical interface to create a reliable AI-powered vision application suitable for research, prototyping, and real-world computer vision applications.
---
👨‍💻 Author

Developed as an AI & Computer Vision Engineering Project

Built using modern machine learning frameworks and professional software development practices.

⭐ If you find this project useful, consider giving it a star!
