import cv2
import numpy as np
from cv2 import aruco


class ArucoProcessor:
    def preprocessing(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        # morphed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return morphed

    def process_frame(self, frame):
        frame = self.preprocessing(frame)
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def get_aruco_distances(self, frame, marker_dict, marker_real_size_meters, camera_matrix, dist_coeffs,
                            parameters=None):
        """
        Функция для обнаружения ArUco маркеров и возврата их ID и расстояния.

        Args:
            frame (np.ndarray): Входной кадр изображения (BGR или серый).
            marker_dict: Объект словаря ArUco (например, aruco.getPredefinedDictionary(aruco.DICT_6X6_250)).
            marker_real_size_meters (float): Длина стороны маркера ArUco в метрах.
            camera_matrix (np.ndarray): Внутренняя матрица камеры (3x3), полученная из калибровки.
            dist_coeffs (np.ndarray): Коэффициенты дисторсии камеры, полученные из калибровки.
            parameters (aruco.DetectorParameters, optional): Параметры детектора. По умолчанию стандартные.

        Returns:
            list[tuple[int, float]]: Список кортежей, где каждый кортеж содержит
                                     (ID маркера, расстояние_в_метрах).
                                     Возвращает пустой список, если маркеры не обнаружены
                                     или произошла ошибка при оценке позы.
        """
        if parameters is None:
            parameters = aruco.DetectorParameters_create()

        # Убедимся, что изображение в оттенках серого
        if len(frame.shape) == 3 and frame.shape[2] == 3:  # Проверяем, если это BGR
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif len(frame.shape) == 2:
            gray = frame  # Уже серый
        else:
            print("Ошибка: Неподдерживаемый формат кадра.")
            return []

        # Обнаружение маркеров
        corners, ids, _ = aruco.detectMarkers(gray,
                                              marker_dict,
                                              parameters=parameters)

        marker_distances = []

        # Если найдены маркеры, оцениваем позу и извлекаем расстояние
        if ids is not None and len(ids) > 0:
            try:
                # Оценка позы требует матрицы камеры и коэффициентов дисторсии
                # Возвращает векторы вращения и трансляции для КАЖДОГО маркера
                rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners,
                                                                  marker_real_size_meters,
                                                                  camera_matrix,
                                                                  dist_coeffs)

                # Извлекаем расстояние (компонент Z вектора трансляции) для каждого маркера
                for i in range(len(ids)):
                    marker_id = int(ids[i][0])
                    # tvecs[i] имеет форму (1, 3), нам нужен Z-компонент tvecs[i][0][2]
                    distance = float(tvecs[i][0][2])
                    marker_distances.append((marker_id, distance))

            except cv2.error as e:
                # Обработка возможных ошибок при оценке позы (например, некорректные данные калибровки)
                print(f"Ошибка при оценке позы ArUco: {e}")
                # В случае ошибки возвращаем пустой список
                return []

        return marker_distances

    def test_aruco(self, frame):

        # Инициализация детектора
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

        # Обнаружение маркеров
        corners, ids, rejected = detector.detectMarkers(frame)

        # Отрисовка обнаруженных маркеров
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # Предположим, у тебя камера 640x480
            fx = fy = 800.0  # Просто предположительное фокусное
            cx = frame.shape[0] / 2
            cy = frame.shape[1] / 2

            camera_matrix = np.array([[fx, 0, cx],
                                      [0, fy, cy],
                                      [0, 0, 1]], dtype=np.float32)

            dist_coeffs = np.zeros(5)  # Дисторсию игнорируем

            marker_length = 0.05
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
            for tvec in tvecs:
                # Расстояние до маркера (по норме вектора)
                distance = np.linalg.norm(tvec[0])
                print(f"Расстояние до маркера: {distance:.2f} м")