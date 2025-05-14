import cv2
import numpy as np

# Создание словаря аруко-маркеров
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Генерация одного маркера
marker_id = 23
marker_size = 200  # пикселей
marker_img = np.zeros((marker_size, marker_size), dtype=np.uint8)
marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size, marker_img, 1)

# Сохранение маркера
cv2.imwrite("out/aruco_marker_23.png", marker_img)