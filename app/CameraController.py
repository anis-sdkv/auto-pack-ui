import threading
import time
from enum import Enum

import cv2
import numpy
import numpy as np

from app.AppConfig import AppConfig
from packing_lib.packing_lib.SceneProcessor import SceneProcessor
from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector, ArucoResult
from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector
from packing_lib.packing_lib.types import PackInputObject


class ActionState(Enum):
    STOPPED = 0
    STARTING = 1
    STARTED = 2
    STOPPING = 3


class CameraController:
    def __init__(self, video_source):
        self.capturing = ActionState.STOPPED
        self.processing = ActionState.STOPPED

        self._video_source = video_source
        self.cap: cv2.VideoCapture | None = None
        boxes_detector = YoloBoxDetector()
        aruco_detector = ArucoBoxDetector(AppConfig.aruco_marker_real_size,
                                          AppConfig.camera_matrix,
                                          AppConfig.dist_coeffs,
                                          AppConfig.aruco_dict)

        self.scene_processor = SceneProcessor(aruco_detector, boxes_detector)

        self.lock = threading.Lock()
        self.latest_frame: numpy.ndarray | None = None
        self.detected_boxes = []
        self.detected_markers: list[ArucoResult] = []
        self.converted_boxes: list[PackInputObject] = []

        self.capture_thread = None
        self.processing_thread = None

        self.on_camera_connected = []
        self.on_camera_connected.append(self._start_capture)

        self.connection_status = "Камера не подключена"

    def start(self):
        self.capturing = ActionState.STARTING
        connecting = threading.Thread(target=self._try_connect_camera,
                                      kwargs={"on_connected_callbacks": self.on_camera_connected},
                                      daemon=True)
        connecting.start()

    def start_processing(self):
        if self.capturing != ActionState.STARTED:
            return
        self.processing = ActionState.STARTING
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()

    def stop_processing(self):
        if self.processing != ActionState.STARTED:
            return
        self.processing = ActionState.STOPPING
        self.processing_thread.join()
        self.detected_boxes = []
        self.detected_markers = []
        self.processing = ActionState.STOPPED

    def stop(self):
        self.stop_processing()

        self.capturing = ActionState.STOPPING
        self.capture_thread.join()
        self.cap.release()
        self.latest_frame = None
        self.capturing = ActionState.STOPPED

    def get_camera_resolution(self) -> tuple[int, int] | None:
        if self.cap is not None and self.cap.isOpened():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return None

    def get_frame(self) -> numpy.ndarray | None:
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

    def get_boxes(self) -> list:
        with self.lock:
            return self.detected_boxes.copy()

    def get_converted_boxes(self):
        with self.lock:
            return self.converted_boxes.copy()

    def get_markers(self) -> list:
        with self.lock:
            return self.detected_markers.copy()

    def _try_connect_camera(self, on_connected_callbacks, max_retries=5, delay=2):
        self.connection_status = "Подключение к камере..."
        for i in range(max_retries):
            self.cap = cv2.VideoCapture(self._video_source)
            if self.cap.isOpened():
                self.connection_status = "Камера успешно подключена."
                for callback in on_connected_callbacks:
                    callback()
                return
            self.connection_status = f"Не удалось подключиться к камере. Повтор через {delay} секунд... (попытка {i + 1}/{max_retries})"
            time.sleep(delay)

        self.connection_status = "Ошибка: Не удалось переподключиться к камере."
        self.capturing = ActionState.STOPPED

    def _start_capture(self):
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

    def _capture_loop(self):
        self.capturing = ActionState.STARTED
        while self.capturing == ActionState.STARTED:
            ret, frame = self.cap.read()
            if not ret:
                continue

            with self.lock:
                self.latest_frame = frame

    def _processing_loop(self):
        self.processing = ActionState.STARTED

        while self.processing == ActionState.STARTED:
            frame = None

            with self.lock:
                if self.latest_frame is not None:
                    frame = self.latest_frame

            if frame is not None:
                result = self.scene_processor.process(frame)

                with self.lock:
                    self.detected_boxes = result.raw_objects
                    self.detected_markers = result.markers
                    self.converted_boxes = result.converted_objects
