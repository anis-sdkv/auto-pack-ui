import cv2


class AppConfig:
    DEFAULT_VIDEO_URL = 'http://192.168.137.43:4747/video'
    ARUCO_DICT = cv2.aruco.DICT_ARUCO_ORIGINAL
    ARUCO_MARKER_REAL_SIZE = 0.023

    def __init__(self):
        self.stream_url = AppConfig.DEFAULT_VIDEO_URL
        self.box_width = 0
        self.box_height = 0
