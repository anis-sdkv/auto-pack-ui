import cv2
import numpy as np


class OpencvBoxDetector:
    def __init__(self, window_name="Controls"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)

        # Создание трекбаров
        cv2.createTrackbar("Blur", self.window_name, 5, 20, self._nothing)
        cv2.createTrackbar("Canny min", self.window_name, 50, 500, self._nothing)
        cv2.createTrackbar("Canny max", self.window_name, 150, 500, self._nothing)
        cv2.createTrackbar("Epsilon %", self.window_name, 2, 10, self._nothing)
        cv2.createTrackbar("Min Area", self.window_name, 1000, 10000, self._nothing)

    def _nothing(self, x):
        pass

    def _get_params(self):
        blur = cv2.getTrackbarPos("Blur", self.window_name)
        blur = blur if blur % 2 == 1 else blur + 1  # нечётное
        canny_min = cv2.getTrackbarPos("Canny min", self.window_name)
        canny_max = cv2.getTrackbarPos("Canny max", self.window_name)
        epsilon_pct = cv2.getTrackbarPos("Epsilon %", self.window_name)
        min_area = cv2.getTrackbarPos("Min Area", self.window_name)
        return blur, canny_min, canny_max, epsilon_pct, min_area

    # def detect_salient(self, image):
    #     # 1. Вычисление карты заметности
    #     saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    #     (success, saliency_map) = saliency.computeSaliency(image)
    #     if not success:
    #         return image  # или исключение
    #
    #     # 2. Бинаризация карты для выделения объектов
    #     thresh_map = cv2.threshold((saliency_map * 255).astype("uint8"), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    #
    #     # 3. Наложение маски на оригинальное изображение
    #     mask = cv2.cvtColor(thresh_map, cv2.COLOR_GRAY2BGR)
    #     highlighted = cv2.addWeighted(image, 0.6, mask, 0.4, 0)
    #
    #     return highlighted

    def detect(self, image):
        blur, canny_min, canny_max, epsilon_pct, min_area = self._get_params()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (blur, blur), 0)
        edges = cv2.Canny(blurred, canny_min, canny_max)

        # ===== Наложение Canny поверх изображения (красным) =====
        edge_overlay = np.zeros_like(image)
        edge_overlay[edges != 0] = [0, 0, 255]  # Красный цвет
        image = cv2.addWeighted(image, 0.5, edge_overlay, 0.9, 0)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            epsilon = (epsilon_pct / 100.0) * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) == 4 and cv2.isContourConvex(approx):
                # area = cv2.contourArea(approx)
                # if area > min_area:
                #     x, y, w, h = cv2.boundingRect(approx)
                #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # зелёная рамка
                rect = cv2.minAreaRect(cnt)  # ((cx, cy), (w, h), angle)
                box = cv2.boxPoints(rect)
                box = box.astype(int)
                cv2.drawContours(image, [box], 0, (0, 255, 0), 2)
        return image
