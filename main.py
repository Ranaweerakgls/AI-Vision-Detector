import sys
import cv2
import time
import torch
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QTimer

from config import (
    DEFAULT_CONFIDENCE,
    DEFAULT_INFERENCE_SIZE,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    SIDE_PANEL_WIDTH,
    VIDEO_EXTENSIONS,
    SCREENSHOT_PREFIX,
    UI_UPDATE_INTERVAL_MS,
    LOADING_ANIMATION_INTERVAL_MS,
)
from config.styles import DARK_THEME_STYLESHEET
from core import DetectionEngine
from ui import VideoDisplay, StatsPanel, ControlPanel, DetectionList, CollapsibleWidget


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Vision Studio")
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self._latest_frame = None
        self._total_detections = 0
        self._current_fps = 0

        self._setup_stylesheet()
        self._setup_ui()
        self._setup_connections()
        self._start_timers()

    def _setup_stylesheet(self):
        self.setStyleSheet(DARK_THEME_STYLESHEET)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        video_container = self._create_video_section()
        main_layout.addWidget(video_container, 1)

        side_panel = self._create_side_panel()
        main_layout.addWidget(side_panel)

        self._detection_engine = DetectionEngine()

    def _create_video_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 10, 20)

        header = self._create_header()
        layout.addLayout(header)

        self._video_display = VideoDisplay()
        layout.addWidget(self._video_display)

        self._loading_label = QLabel("")
        self._loading_label.setObjectName("loadingLabel")
        self._loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._loading_label)

        return container

    def _create_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 10)

        title = QLabel("AI VISION STUDIO")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self._fps_label = QLabel("FPS: --")
        self._fps_label.setObjectName("fpsLabel")
        header.addWidget(self._fps_label)

        return header

    def _create_side_panel(self):
        panel = QWidget()
        panel.setObjectName("sidePanel")
        panel.setFixedWidth(SIDE_PANEL_WIDTH)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        header = self._create_panel_header()
        layout.addWidget(header)

        self._stats_panel = StatsPanel()
        layout.addWidget(self._stats_panel)

        self._control_panel = ControlPanel()
        layout.addWidget(self._control_panel.widget)

        detections = CollapsibleWidget("Detections")
        self._detection_list = DetectionList()
        detections.content_layout.addWidget(self._detection_list)
        layout.addWidget(detections)

        layout.addStretch()
        return panel

    def _create_panel_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("🎯")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 16px;")
        layout.addWidget(logo)

        subtitle = QLabel("Object Detection")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        return header

    def _setup_connections(self):
        cp = self._control_panel
        cp.start_btn.clicked.connect(self._start_detection)
        cp.stop_btn.clicked.connect(self._stop_detection)
        cp.screenshot_btn.clicked.connect(self._save_screenshot)
        cp.record_btn.clicked.connect(self._toggle_record)

        cp.conf_slider.valueChanged.connect(lambda v: self._update_conf_value(v))
        cp.size_slider.valueChanged.connect(lambda v: self._update_size_value(v))

        cp.source_combo.currentIndexChanged.connect(self._on_source_changed)
        cp.device_combo.currentTextChanged.connect(self._on_device_changed)

        self._detection_engine.frame_ready.connect(self._on_new_frame)
        self._detection_engine.counter_updated.connect(self._update_counter)
        self._detection_engine.loading_status.connect(self._handle_loading)
        self._detection_engine.fps_updated.connect(self._update_fps)

    def _start_timers(self):
        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._animate_loading)
        self._dot_count = 0

        self._ui_timer = QTimer()
        self._ui_timer.timeout.connect(self._update_display)
        self._ui_timer.start(UI_UPDATE_INTERVAL_MS)

    def _animate_loading(self):
        dots = "." * (self._dot_count % 4)
        self._loading_label.setText(f"Loading model{dots}")
        self._dot_count += 1

    def _handle_loading(self, msg):
        if msg == "start":
            self._control_panel.start_btn.setEnabled(False)
            self._loading_timer.start(LOADING_ANIMATION_INTERVAL_MS)
        else:
            self._loading_timer.stop()
            self._loading_label.setText("Ready ✓")
            self._control_panel.start_btn.setEnabled(True)

    def _on_source_changed(self, index):
        if index == 1:
            choice = QFileDialog.getOpenFileName(self, "Select Video", "", VIDEO_EXTENSIONS)[0]
            if choice:
                self._detection_engine.source = choice
                self._control_panel.source_combo.setCurrentText("Video File")
            else:
                self._control_panel.source_combo.setCurrentIndex(0)

    def _on_device_changed(self, text):
        device = "cuda" if text == "GPU" else "cpu"
        self._detection_engine.set_device(device)

    def _start_detection(self):
        source = 0 if self._control_panel.source_combo.currentIndex() == 0 else self._detection_engine.source
        self._detection_engine.source = source
        self._detection_engine.conf_threshold = self._control_panel.conf_slider.value() / 100
        self._detection_engine.inference_size = self._control_panel.size_slider.value()
        self._detection_engine.running = True
        self._detection_engine.start()
        self._total_detections = 0

    def _stop_detection(self):
        self._detection_engine.stop()
        self._latest_frame = None
        self._loading_label.setText("")

    def _on_new_frame(self, frame):
        self._latest_frame = frame.copy()

    def _update_display(self):
        if self._latest_frame is not None:
            self._video_display.update_frame(self._latest_frame)

    def _update_counter(self, counter):
        self._detection_list.update_items(counter)
        total = sum(counter.values())
        self._total_detections += total
        self._stats_panel.update_stats(self._current_fps, total, self._total_detections)

    def _update_fps(self, fps):
        self._current_fps = fps
        self._fps_label.setText(f"FPS: {fps:.1f}")

    def _save_screenshot(self):
        if self._latest_frame is not None:
            filename = f"{SCREENSHOT_PREFIX}{int(time.time())}.png"
            cv2.imwrite(filename, self._latest_frame)
            self._loading_label.setText(f"Saved: {filename}")

    def _toggle_record(self):
        cp = self._control_panel
        if not self._detection_engine.recording:
            if self._latest_frame is not None:
                self._detection_engine.start_recording(self._latest_frame.shape)
                cp.record_btn.setText("⏹  Stop Recording")
                self._loading_label.setText("Recording...")
        else:
            self._detection_engine.stop_recording()
            cp.record_btn.setText("⏺  Record")
            self._loading_label.setText("Recording saved!")

    def _update_conf_value(self, value):
        self._control_panel.conf_value.setText(f"{value}%")

    def _update_size_value(self, value):
        self._control_panel.size_value.setText(f"{value}px")

    def closeEvent(self, event):
        self._ui_timer.stop()
        self._detection_engine.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
