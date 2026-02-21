import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QSlider, QComboBox, QFrame, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor

from config import (
    DEFAULT_CONFIDENCE,
    DEFAULT_INFERENCE_SIZE,
    MIN_INFERENCE_SIZE,
    MAX_INFERENCE_SIZE,
    SIDE_PANEL_WIDTH,
    VIDEO_EXTENSIONS,
    SCREENSHOT_PREFIX,
)
from config.styles import DARK_THEME_STYLESHEET
from core.detection import DetectionEngine, ColorManager
from ui.components import CollapsibleWidget


class VideoDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("videoContainer")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMinimumSize(800, 600)
        self._layout.addWidget(self._image_label)

    def update_frame(self, frame):
        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            scaled = QPixmap.fromImage(qt_img).scaled(
                self._image_label.width(), self._image_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._image_label.setPixmap(scaled)


class StatsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statsCard")
        self._layout = QHBoxLayout(self)

        self._fps_widget = self._create_stat_widget("0", "FPS")
        self._objs_widget = self._create_stat_widget("0", "Objects")
        self._total_widget = self._create_stat_widget("0", "Total")

        self._layout.addWidget(self._fps_widget)
        self._layout.addWidget(self._objs_widget)
        self._layout.addWidget(self._total_widget)

    def _create_stat_widget(self, value, label):
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

    def update_stats(self, fps, objects, total):
        self._fps_widget.findChild(QLabel).setText(f"{fps:.0f}")
        self._objs_widget.findChild(QLabel).setText(str(objects))
        self._total_widget.findChild(QLabel).setText(str(total))


class ControlPanel:
    def __init__(self, parent=None):
        import torch
        
        self._widget = CollapsibleWidget("Controls")
        self._source_combo = QComboBox()
        self._source_combo.addItems(["Webcam", "Select Video File"])

        self._device_combo = QComboBox()
        self._device_combo.addItem("CPU")
        try:
            if torch.cuda.is_available():
                self._device_combo.addItem("GPU")
        except Exception:
            pass

        self._conf_slider = QSlider(Qt.Horizontal)
        self._conf_slider.setMinimum(1)
        self._conf_slider.setMaximum(100)
        self._conf_slider.setValue(int(DEFAULT_CONFIDENCE * 100))
        self._conf_slider.setFixedHeight(10)

        self._conf_value = QLabel(f"{int(DEFAULT_CONFIDENCE * 100)}%")

        self._size_slider = QSlider(Qt.Horizontal)
        self._size_slider.setMinimum(MIN_INFERENCE_SIZE)
        self._size_slider.setMaximum(MAX_INFERENCE_SIZE)
        self._size_slider.setValue(DEFAULT_INFERENCE_SIZE)
        self._size_slider.setSingleStep(320)
        self._size_slider.setFixedHeight(10)

        self._size_value = QLabel(f"{DEFAULT_INFERENCE_SIZE}px")

        self._start_btn = QPushButton("▶  Start Detection")
        self._stop_btn = QPushButton("⏹  Stop")
        self._screenshot_btn = QPushButton("📷  Screenshot")
        self._record_btn = QPushButton("⏺  Record")

        self._build_ui()

    def _build_ui(self):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._create_label("Source"))
        layout.addWidget(self._source_combo)

        layout.addWidget(self._create_label("Device"))
        layout.addWidget(self._device_combo)

        layout.addWidget(self._create_label("Confidence"))
        layout.addWidget(self._conf_slider)
        layout.addWidget(self._conf_value)

        layout.addWidget(self._create_label("Resolution"))
        layout.addWidget(self._size_slider)
        layout.addWidget(self._size_value)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._start_btn)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)

        btn_layout2 = QHBoxLayout()
        btn_layout2.addWidget(self._screenshot_btn)
        btn_layout2.addWidget(self._record_btn)
        layout.addLayout(btn_layout2)

        self._widget.content_layout.addWidget(content)

    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("section-label")
        return lbl

    @property
    def widget(self):
        return self._widget

    @property
    def source_combo(self):
        return self._source_combo

    @property
    def device_combo(self):
        return self._device_combo

    @property
    def conf_slider(self):
        return self._conf_slider

    @property
    def conf_value(self):
        return self._conf_value

    @property
    def size_slider(self):
        return self._size_slider

    @property
    def size_value(self):
        return self._size_value

    @property
    def start_btn(self):
        return self._start_btn

    @property
    def stop_btn(self):
        return self._stop_btn

    @property
    def screenshot_btn(self):
        return self._screenshot_btn

    @property
    def record_btn(self):
        return self._record_btn


class DetectionList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detectionList")
        self._color_manager = ColorManager()

    def update_items(self, counter):
        self.clear()
        for label, count in sorted(counter.items()):
            color = self._color_manager.get_color(label)
            item = QListWidgetItem(f"  {label}: {count}")
            item.setForeground(QColor(color))
            self.addItem(item)
