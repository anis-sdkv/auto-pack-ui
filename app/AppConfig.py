import cv2
import numpy as np


class AppConfig:
    @staticmethod
    def camera_matrix():
        frame_shape = (640, 480)
        fx = fy = 800.0
        cx = frame_shape[0] / 2
        cy = frame_shape[1] / 2

        return np.array([[fx, 0, cx],
                         [0, fy, cy],
                         [0, 0, 1]], dtype=np.float64)

    @staticmethod
    def dist_coeffs():
        return np.zeros((5, 1), dtype=np.float64)

    stream_url = 'http://192.168.137.60:4747/video'
    box_width = 0.4
    box_height = 0.4
    aruco_marker_real_size = 0.023
    aruco_dict = cv2.aruco.DICT_ARUCO_ORIGINAL
    camera_matrix = camera_matrix()
    dist_coeffs = dist_coeffs()
