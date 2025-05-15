import threading
import time
from enum import Enum

import cv2
import numpy
import numpy as np

from app.AppConfig import AppConfig
from camera.detectors.ArucoDetector import ArucoBoxDetector, ArucoResult
from camera.detectors.YoloBoxDetector import YoloBoxDetector


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
        self.boxes_detector = YoloBoxDetector()
        self.aruco_detector = ArucoBoxDetector(AppConfig.ARUCO_MARKER_REAL_SIZE, AppConfig.ARUCO_DICT)

        self.lock = threading.Lock()
        self.latest_frame: numpy.ndarray | None = None
        self.detected_boxes = []
        self.detected_markers: list[ArucoResult] = []

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
                detected_boxes = self.boxes_detector.detect(frame)
                detected_markers = self.aruco_detector.detect(frame)

                boxes_filtered = self.filter_by_overlap(detected_boxes, [m.bounding_box for m in detected_markers])
                with self.lock:
                    self.detected_boxes = boxes_filtered
                    self.detected_markers = detected_markers

    def filter_by_overlap(self, source_list, remove_list, threshold=0.8):
        filtered = []
        for src in source_list:
            if not any(self.box_inside_area_ratio(rem, src) > threshold for rem in remove_list):
                filtered.append(src)
        return filtered

    @staticmethod
    def box_inside_area_ratio(inner_box: np.ndarray, outer_box: np.ndarray) -> float:
        inner_box = np.array(inner_box, dtype=np.float32)
        outer_box = np.array(outer_box, dtype=np.float32)

        inter_area, _ = cv2.intersectConvexConvex(inner_box, outer_box)

        inner_area = cv2.contourArea(inner_box)

        if inner_area == 0:
            return 0.0

        print(inter_area / inner_area)
        return inter_area / inner_area
