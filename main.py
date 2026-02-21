import sys
import cv2
import torch
import time
import numpy as np
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QSlider, QComboBox, QFrame, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QColor


COLORS = ['#38bdf8', '#10b981', '#f97316', '#8b5cf6', '#ec4899', '#ef4444', '#84cc16', '#06b6d4']
CLASS_COLORS = {}

def get_class_color(cls_name):
    if cls_name not in CLASS_COLORS:
        CLASS_COLORS[cls_name] = COLORS[len(CLASS_COLORS) % len(COLORS)]
    return CLASS_COLORS[cls_name]


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(object)
    update_counter_signal = pyqtSignal(dict)
    loading_signal = pyqtSignal(str)
    fps_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.running = False
        self.conf_threshold = 0.25
        self.device = 'cpu'
        self.source = 0
        self.recording = False
        self.out = None
        self.inference_size = 640
        self.model = None
        self.model_loaded = False

    def load_model(self):
        if not self.model_loaded:
            self.loading_signal.emit("start")
            self.model = YOLO("yolov8n.pt", task="detect")
            self.model.to(self.device)
            self.model_loaded = True
            self.loading_signal.emit("finished")

    def run(self):
        self.load_model()
        
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            return
        
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        frame_times = []
        
        while self.running:
            loop_start = time.time()
            
            ret, frame = cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            scale = self.inference_size / max(w, h)
            inference_frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR) if scale < 1 else frame
            
            results = self.model(inference_frame, stream=True, conf=self.conf_threshold, verbose=False)
            counter = {}
            
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    label = self.model.names[cls]
                    counter[label] = counter.get(label, 0) + 1
                    
                    x1, y1, x2, y2 = box.xyxy[0]
                    if scale < 1:
                        x1, y1, x2, y2 = int(x1 / scale), int(y1 / scale), int(x2 / scale), int(y2 / scale)
                    else:
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    conf = float(box.conf[0])
                    color = get_class_color(label)
                    c = QColor(color)
                    color_rgb = (c.red(), c.green(), c.blue())
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color_rgb, 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_rgb, 2)
            
            if self.recording and self.out:
                self.out.write(frame)
            
            self.update_counter_signal.emit(counter)
            self.change_pixmap_signal.emit(frame)
            
            frame_times.append(time.time() - loop_start)
            if len(frame_times) >= 10:
                fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else 0
                self.fps_signal.emit(fps)
                frame_times = []
        
        cap.release()
        if self.out:
            self.out.release()

    def stop(self):
        self.running = False
        self.wait()

    def set_device(self, device):
        self.device = device
        if self.model_loaded and self.model:
            self.model.to(device)

    def start_recording(self, frame_shape):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter("output.avi", fourcc, 20.0, (frame_shape[1], frame_shape[0]))
        self.recording = True

    def stop_recording(self):
        self.recording = False
        if self.out:
            self.out.release()
            self.out = None


class CollapsibleWidget(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("collapsible")
        self.expanded = True
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.header = QPushButton(f"▼ {title}")
        self.header.setObjectName("collapsibleHeader")
        self.header.clicked.connect(self.toggle)
        self.main_layout.addWidget(self.header)
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.addWidget(self.content)
        
        self.header.setCursor(Qt.PointingHandCursor)
    
    def toggle(self):
        self.expanded = not self.expanded
        self.content.setVisible(self.expanded)
        arrow = "▼" if self.expanded else "▶"
        title = self.header.text()[2:]
        self.header.setText(f"{arrow} {title}")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Vision Studio")
        self.resize(1400, 900)
        self.latest_frame = None
        self.total_detections = 0
        
        self.setup_stylesheet()
        self.setup_ui()
        self.setup_connections()
        self.start_timers()

    def setup_stylesheet(self):
        self.setStyleSheet("""
            * { font-family: 'Segoe UI', sans-serif; }
            QWidget { background-color: #0a0a0a; color: #e0e0e0; }
            QPushButton {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #252525;
                border-color: #38bdf8;
            }
            QPushButton:pressed {
                background-color: #38bdf8;
                color: #000;
            }
            QPushButton:disabled { opacity: 0.5; }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1a1a1a;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #38bdf8;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QComboBox {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QComboBox:hover { border-color: #38bdf8; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                selection-background-color: #38bdf8;
            }
            #videoContainer {
                background-color: #000;
                border-radius: 12px;
                border: 1px solid #1a1a1a;
            }
            #sidePanel {
                background-color: #0f0f0f;
                border-left: 1px solid #1a1a1a;
            }
            #collapsible { background-color: #141414; border-radius: 8px; margin: 4px 0; }
            #collapsibleHeader {
                background-color: transparent;
                border: none;
                text-align: left;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #38bdf8;
                padding: 12px;
            }
            #collapsibleHeader:hover { background-color: transparent; }
            #detectionList QListWidget {
                background-color: transparent;
                border: none;
                font-size: 13px;
            }
            #detectionList QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            #detectionList QListWidget::item:hover { background-color: #1a1a1a; }
            #statsCard { background-color: #141414; border-radius: 10px; padding: 10px; }
            #statValue { font-size: 22px; font-weight: bold; color: #38bdf8; }
            #statLabel { font-size: 10px; color: #666; text-transform: uppercase; }
            #titleLabel { font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #fff; }
            #subtitleLabel { font-size: 11px; color: #555; }
            #fpsLabel { font-size: 13px; font-weight: 600; color: #10b981; }
            #loadingLabel { font-size: 13px; color: #38bdf8; font-weight: 500; }
            .section-label { color: #666; font-size: 10px; text-transform: uppercase; margin-top: 8px; }
        """)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        video_container = QWidget()
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(20, 20, 10, 20)
        
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("AI VISION STUDIO")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setObjectName("fpsLabel")
        header.addWidget(self.fps_label)
        
        video_layout.addLayout(header)
        
        self.video_frame = QFrame()
        self.video_frame.setObjectName("videoContainer")
        self.video_layout = QVBoxLayout(self.video_frame)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 600)
        self.video_layout.addWidget(self.image_label)
        
        video_layout.addWidget(self.video_frame, 1)
        
        self.loading_label = QLabel("")
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignCenter)
        video_layout.addWidget(self.loading_label)
        
        main_layout.addWidget(video_container, 1)
        
        self.side_panel = QWidget()
        self.side_panel.setObjectName("sidePanel")
        self.side_panel.setFixedWidth(320)
        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setContentsMargins(15, 20, 15, 20)
        side_layout.setSpacing(10)
        
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        logo = QLabel("🎯")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(logo)
        
        subtitle = QLabel("Object Detection")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)
        
        side_layout.addWidget(header_widget)
        
        side_layout.addSpacing(10)
        
        stats = self.create_stats_section()
        side_layout.addWidget(stats)
        
        self.controls = CollapsibleWidget("Controls")
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Webcam", "Select Video File"])
        
        self.device_combo = QComboBox()
        self.device_combo.addItem("CPU")
        if torch.cuda.is_available():
            self.device_combo.addItem("GPU")
        
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setMinimum(1)
        self.conf_slider.setMaximum(100)
        self.conf_slider.setValue(25)
        self.conf_slider.setFixedHeight(10)
        
        self.conf_value = QLabel("25%")
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(320)
        self.size_slider.setMaximum(1280)
        self.size_slider.setValue(640)
        self.size_slider.setSingleStep(320)
        self.size_slider.setFixedHeight(10)
        
        self.size_value = QLabel("640px")
        
        controls_content = QWidget()
        controls_layout = QVBoxLayout(controls_content)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        l = QLabel("Source"); l.setObjectName("section-label"); controls_layout.addWidget(l)
        controls_layout.addWidget(self.source_combo)
        
        l = QLabel("Device"); l.setObjectName("section-label"); controls_layout.addWidget(l)
        controls_layout.addWidget(self.device_combo)
        
        l = QLabel("Confidence"); l.setObjectName("section-label"); controls_layout.addWidget(l)
        controls_layout.addWidget(self.conf_slider)
        controls_layout.addWidget(self.conf_value)
        
        l = QLabel("Resolution"); l.setObjectName("section-label"); controls_layout.addWidget(l)
        controls_layout.addWidget(self.size_slider)
        controls_layout.addWidget(self.size_value)
        
        self.start_btn = QPushButton("▶  Start Detection")
        self.stop_btn = QPushButton("⏹  Stop")
        self.screenshot_btn = QPushButton("📷  Screenshot")
        self.record_btn = QPushButton("⏺  Record")
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        controls_layout.addLayout(btn_layout)
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.addWidget(self.screenshot_btn)
        btn_layout2.addWidget(self.record_btn)
        controls_layout.addLayout(btn_layout2)
        
        self.controls.content_layout.addWidget(controls_content)
        side_layout.addWidget(self.controls)
        
        detections = CollapsibleWidget("Detections")
        
        self.detection_list = QListWidget()
        self.detection_list.setObjectName("detectionList")
        detections.content_layout.addWidget(self.detection_list)
        
        side_layout.addWidget(detections)
        
        side_layout.addStretch()
        
        main_layout.addWidget(self.side_panel)
        
        self.thread = VideoThread()

    def create_stats_section(self):
        stats_container = QWidget()
        stats_container.setObjectName("statsCard")
        stats_layout = QHBoxLayout(stats_container)
        
        self.fps_stat = self.create_stat_widget("0", "FPS")
        self.objs_stat = self.create_stat_widget("0", "Objects")
        self.total_stat = self.create_stat_widget("0", "Total")
        
        stats_layout.addWidget(self.fps_stat)
        stats_layout.addWidget(self.objs_stat)
        stats_layout.addWidget(self.total_stat)
        
        return stats_container

    def create_stat_widget(self, value, label):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        
        val = QLabel(value)
        val.setObjectName("statValue")
        val.setAlignment(Qt.AlignCenter)
        layout.addWidget(val)
        
        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        return widget

    def setup_connections(self):
        self.start_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)
        self.screenshot_btn.clicked.connect(self.save_screenshot)
        self.record_btn.clicked.connect(self.toggle_record)
        
        self.conf_slider.valueChanged.connect(lambda v: self.conf_value.setText(f"{v}%"))
        self.size_slider.valueChanged.connect(lambda v: self.size_value.setText(f"{v}px"))
        
        self.source_combo.currentIndexChanged.connect(self.on_source_changed)
        self.device_combo.currentTextChanged.connect(lambda t: self.thread.set_device("cuda" if t == "GPU" else "cpu"))
        
        self.thread.change_pixmap_signal.connect(self.on_new_frame)
        self.thread.update_counter_signal.connect(self.update_counter)
        self.thread.loading_signal.connect(self.handle_loading)
        self.thread.fps_signal.connect(self.update_fps)

    def start_timers(self):
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_loading)
        self.dot_count = 0
        
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_display)
        self.ui_timer.start(33)

    def animate_loading(self):
        dots = "." * (self.dot_count % 4)
        self.loading_label.setText(f"Loading model{dots}")
        self.dot_count += 1

    def handle_loading(self, msg):
        if msg == "start":
            self.start_btn.setEnabled(False)
            self.loading_timer.start(300)
        else:
            self.loading_timer.stop()
            self.loading_label.setText("Ready ✓")
            self.start_btn.setEnabled(True)

    def on_source_changed(self, index):
        if index == 1:
            choice = QFileDialog.getOpenFileName(self, "Select Video", "", "Videos (*.mp4 *.avi *.mov)")[0]
            if choice:
                self.thread.source = choice
                self.source_combo.setCurrentText("Video File")
            else:
                self.source_combo.setCurrentIndex(0)

    def start_detection(self):
        self.thread.source = 0 if self.source_combo.currentIndex() == 0 else self.thread.source
        self.thread.conf_threshold = self.conf_slider.value() / 100
        self.thread.inference_size = self.size_slider.value()
        self.thread.running = True
        self.thread.start()
        self.total_detections = 0

    def stop_detection(self):
        self.thread.stop()
        self.latest_frame = None
        self.loading_label.setText("")

    def on_new_frame(self, frame):
        self.latest_frame = frame.copy()

    def update_display(self):
        if self.latest_frame is not None:
            rgb = cv2.cvtColor(self.latest_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            scaled = QPixmap.fromImage(qt_img).scaled(
                self.image_label.width(), self.image_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

    def update_counter(self, counter):
        self.detection_list.clear()
        total = 0
        
        for label, count in sorted(counter.items()):
            total += count
            color = get_class_color(label)
            
            item = QListWidgetItem(f"  {label}: {count}")
            item.setForeground(QColor(color))
            self.detection_list.addItem(item)
        
        self.total_detections += total
        
        for w, val in [(self.objs_stat, total), (self.total_stat, self.total_detections)]:
            w.findChild(QLabel).setText(str(val))

    def update_fps(self, fps):
        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.fps_stat.findChild(QLabel).setText(f"{fps:.0f}")

    def save_screenshot(self):
        if self.latest_frame is not None:
            filename = f"screenshot_{int(time.time())}.png"
            cv2.imwrite(filename, self.latest_frame)
            self.loading_label.setText(f"Saved: {filename}")

    def toggle_record(self):
        if not self.thread.recording:
            if self.latest_frame is not None:
                self.thread.start_recording(self.latest_frame.shape)
                self.record_btn.setText("⏹  Stop Recording")
                self.loading_label.setText("Recording...")
        else:
            self.thread.stop_recording()
            self.record_btn.setText("⏺  Record")
            self.loading_label.setText("Recording saved!")

    def closeEvent(self, event):
        self.ui_timer.stop()
        self.thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
