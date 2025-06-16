# import cv2
# import numpy as np
#
# from app.common import Colors
# from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector
# from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector
#
#
# def filter_by_overlap(source_list, remove_list, threshold=0.8):
#     filtered = []
#     for src in source_list:
#         if not any(box_inside_area_ratio(rem, src.bounding_box) > threshold for rem in remove_list):
#             filtered.append(src)
#     return filtered
#
#
# def box_inside_area_ratio(inner_box: np.ndarray, outer_box: np.ndarray) -> float:
#     inner_box = np.array(inner_box, dtype=np.float32)
#     outer_box = np.array(outer_box, dtype=np.float32)
#
#     inter_area, _ = cv2.intersectConvexConvex(inner_box, outer_box)
#
#     inner_area = cv2.contourArea(inner_box)
#
#     if inner_area == 0:
#         return 0.0
#
#     print(inter_area / inner_area)
#     return inter_area / inner_area
#
#
# def process(path):
#     boxes_detector = YoloBoxDetector()
#     aruco_detector = ArucoBoxDetector(2.3)
#
#     frame = cv2.imread(path)
#
#     boxes = boxes_detector.detect(frame)
#     markers = [i.bounding_box for i in aruco_detector.detect(frame)]
#     boxes_filtered = filter_by_overlap(boxes, markers)
#
#     for b in boxes_filtered:
#         if b is not None and len(b) > 0:
#             b = np.array(b, dtype=np.int32)
#             if b.ndim == 2:
#                 b = b.reshape((-1, 1, 2))  # формат для drawContours
#         cv2.drawContours(frame, [b], 0, Colors.GREEN, 2)
#
#     for b in markers:
#         if b is not None and len(b) > 0:
#             b = np.array(b, dtype=np.int32)
#             if b.ndim == 2:
#                 b = b.reshape((-1, 1, 2))  # формат для drawContours
#         cv2.drawContours(frame, [b], 0, (0, 0, 255), 2)
#
#     cv2.imwrite("out/detect.png", frame)
