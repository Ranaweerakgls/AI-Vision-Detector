import cv2
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor
from ultralytics import YOLO

from config import (
    DETECTION_COLORS,
    DEFAULT_CONFIDENCE,
    DEFAULT_INFERENCE_SIZE,
    MODEL_PATH,
    OUTPUT_VIDEO,
    FPS_CALCULATION_FRAMES,
    VIDEO_FPS,
)


class ColorManager:
    _instance = None
    _class_colors = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_color(self, cls_name):
        if cls_name not in self._class_colors:
            self._class_colors[cls_name] = DETECTION_COLORS[len(self._class_colors) % len(DETECTION_COLORS)]
        return self._class_colors[cls_name]

    def get_rgb(self, cls_name):
        color = self.get_color(cls_name)
        c = QColor(color)
        return (c.red(), c.green(), c.blue())

    def reset(self):
        self._class_colors = {}


class DetectionEngine(QThread):
    frame_ready = pyqtSignal(object)
    counter_updated = pyqtSignal(dict)
    loading_status = pyqtSignal(str)
    fps_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._running = False
        self._conf_threshold = DEFAULT_CONFIDENCE
        self._device = 'cpu'
        self._source = 0
        self._recording = False
        self._video_writer = None
        self._inference_size = DEFAULT_INFERENCE_SIZE
        self._model = None
        self._model_loaded = False
        self._color_manager = ColorManager()

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def conf_threshold(self):
        return self._conf_threshold

    @conf_threshold.setter
    def conf_threshold(self, value):
        self._conf_threshold = value

    @property
    def inference_size(self):
        return self._inference_size

    @inference_size.setter
    def inference_size(self, value):
        self._inference_size = value

    @property
    def recording(self):
        return self._recording

    def load_model(self):
        if not self._model_loaded:
            self.loading_status.emit("start")
            self._model = YOLO(MODEL_PATH, task="detect")
            self._model.to(self._device)
            self._model_loaded = True
            self.loading_status.emit("finished")

    def run(self):
        self.load_model()
        self._color_manager.reset()

        cap = cv2.VideoCapture(self._source)
        if not cap.isOpened():
            return

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        frame_times = []

        while self._running:
            loop_start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = self._process_frame(frame)

            if self._recording and self._video_writer:
                self._video_writer.write(frame)

            frame_times.append(time.time() - loop_start)
            if len(frame_times) >= FPS_CALCULATION_FRAMES:
                fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else 0
                self.fps_updated.emit(fps)
                frame_times = []

        cap.release()
        if self._video_writer:
            self._video_writer.release()

    def _process_frame(self, frame):
        h, w = frame.shape[:2]
        scale = self._inference_size / max(w, h)
        inference_frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR) if scale < 1 else frame

        results = self._model(inference_frame, stream=True, conf=self._conf_threshold, verbose=False)
        counter = {}

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = self._model.names[cls]
                counter[label] = counter.get(label, 0) + 1

                x1, y1, x2, y2 = box.xyxy[0]
                if scale < 1:
                    x1, y1, x2, y2 = int(x1 / scale), int(y1 / scale), int(x2 / scale), int(y2 / scale)
                else:
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                conf = float(box.conf[0])
                color_rgb = self._color_manager.get_rgb(label)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color_rgb, 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_rgb, 2)

        self.counter_updated.emit(counter)
        self.frame_ready.emit(frame)
        return frame

    def stop(self):
        self._running = False
        self.wait()

    def set_device(self, device):
        self._device = device
        if self._model_loaded and self._model:
            self._model.to(device)

    def start_recording(self, frame_shape):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self._video_writer = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, VIDEO_FPS, (frame_shape[1], frame_shape[0]))
        self._recording = True

    def stop_recording(self):
        self._recording = False
        if self._video_writer:
            self._video_writer.release()
            self._video_writer = None
