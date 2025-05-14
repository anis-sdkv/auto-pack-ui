import cv2
import numpy as np


class ArucoResult:
    def __init__(self, id, bbox, rvec, tvec ):
        self.id = id
        self.bounding_box = bbox
        self.rvec =rvec
        self.tvec = tvec


class ArucoBoxDetector:
    def __init__(self, marker_real_size, dict_type=cv2.aruco.DICT_ARUCO_ORIGINAL):
        self.marker_dict = cv2.aruco.getPredefinedDictionary(dict_type)
        self.marker_real_size = marker_real_size
        self.parameters = cv2.aruco.DetectorParameters()

    def detect(self, frame) -> list[ArucoResult]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.marker_dict, parameters=self.parameters)

        results = []
        if ids is None or len(corners) == 0:
            return results

        camera_matrix, dist_coeffs = self._get_camera_calibration_params(frame.shape)
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.marker_real_size,
                                                              camera_matrix, dist_coeffs)

        for i, marker_corners in enumerate(corners):
            marker_corners = marker_corners[0].astype(np.int32)

            result = ArucoResult(
                id=int(ids[i][0]),
                bbox=self.get_rotated_bbox_from_corners(marker_corners),
                rvec=rvecs[i],
                tvec=tvecs[i]
            )
            results.append(result)

        return results

    def get_rotated_bbox_from_corners(self, marker_corners):
        rect = cv2.minAreaRect(marker_corners)
        return cv2.boxPoints(rect)

    def _get_camera_calibration_params(self, frame_shape):

        fx = fy = 800.0  # Предположительное фокусное
        cx = frame_shape[0] / 2
        cy = frame_shape[1] / 2

        camera_matrix = np.array([[fx, 0, cx],
                                  [0, fy, cy],
                                  [0, 0, 1]], dtype=np.float32)

        dist_coeffs = np.zeros(5)  # Дисторсию игнорируем
        return camera_matrix, dist_coeffs
