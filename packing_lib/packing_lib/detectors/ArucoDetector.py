import cv2
import numpy as np

from packing_lib.packing_lib.types import ArucoResult


class ArucoBoxDetector:
    def __init__(self, aruco_size_mm: float, cam_matrix, cam_dist, dict_type=cv2.aruco.DICT_ARUCO_ORIGINAL):
        self.marker_dict = cv2.aruco.getPredefinedDictionary(dict_type)
        self.aruco_size_mm: float = aruco_size_mm
        self.parameters = cv2.aruco.DetectorParameters()
        self.camera_matrix = cam_matrix
        self.dist = cam_dist

    def detect(self, frame) -> list[ArucoResult]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.marker_dict, parameters=self.parameters)

        results = []
        if ids is None or len(corners) == 0:
            return results

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.aruco_size_mm,
                                                              self.camera_matrix, self.dist)

        for i, marker_corners in enumerate(corners):
            marker_corners = marker_corners[0].astype(np.int32)

            result = ArucoResult(
                id=int(ids[i][0]),
                bounding_box=self.get_rotated_bbox_from_corners(marker_corners),
                rvec=rvecs[i],
                tvec=tvecs[i]
            )
            results.append(result)

        return results

    @staticmethod
    def get_rotated_bbox_from_corners(marker_corners):
        rect = cv2.minAreaRect(marker_corners)
        return cv2.boxPoints(rect)