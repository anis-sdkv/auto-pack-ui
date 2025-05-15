import cv2
import numpy as np
import torch
from ultralytics import YOLO


class YoloBoxDetector:
    def __init__(self, model_path="FastSAM-s.pt", conf_threshold=0.6):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        results = self.model.predict(
            source=frame,  # путь к изображению, видео, папке, rtsp, 0 (камера)
            conf=self.conf_threshold,  # порог уверенности (Confidence threshold)
            device='cpu',  # 'cpu', '0', '0,1' — номер GPU или 'cpu'
            imgsz=frame.shape[1],  # размер входного изображения
            # iou=0.8,  # порог IoU для NMS (Non-Maximum Suppression)
            # classes=[0, 2],  # детектировать только определённые классы (по индексам)
            # save=True,  # сохранить результат в файл
            # save_txt=True,  # сохранить результаты в txt (в формате YOLO)
            # save_crop=True,  # сохранить обрезанные изображения объектов
            # show=True,  # показать окно с результатом
            # stream=False,  # если True, возвращает генератор (для обработки кадров)
            # max_det=100,  # максимальное число объектов на изображении
            # verbose=False,  # логировать ли в консоль
        )
        boxes = []
        if len(results) == 0:
            return boxes

        result = results[0]
        img = frame.copy()

        if result.masks is None or result.masks.data is None or result.masks.data.shape[0] > 50:
            print("ret")
            return boxes

        masks = result.masks.data.cpu().numpy()  # (N, H, W)
        masks  = self.remove_inner_masks(masks)
        num_masks = masks.shape[0]

        colors = [(255, 0, 0) for _ in range(num_masks)]

        for i in range(num_masks):
            mask = masks[i]
            color = colors[i]

            if mask.shape != img.shape[:2]:
                mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)

            colored_mask = np.zeros_like(img, dtype=np.uint8)
            for c in range(3):
                colored_mask[:, :, c] = mask * color[c]

            boxes.append(self.get_rotated_bbox_from_mask(mask))
        return boxes

    def get_rotated_bbox_from_mask(self, mask):
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        cnt = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(cnt)
        return cv2.boxPoints(rect)  # ((cx, cy), (w, h), angle)


    def remove_inner_masks(self, masks, iou_thresh=0.9, min_area=100):
        """
        Удаляет маски, вложенные в более крупные, и возвращает отфильтрованные маски.

        :param masks: np.ndarray shape (N, H, W) — бинарные маски
        :param iou_thresh: порог перекрытия (IoU), при котором маска считается вложенной
        :param min_area: минимальная площадь маски, чтобы она считалась значимой
        :return: np.ndarray отфильтрованных масок
        """
        N = masks.shape[0]
        areas = [np.sum(m) for m in masks]
        indices = list(range(N))

        sorted_idxs = sorted(indices, key=lambda i: -areas[i])  # от больших к меньшим

        keep = []
        removed = set()

        for i in sorted_idxs:
            if i in removed or areas[i] < min_area:
                continue
            keep.append(i)
            mi = masks[i]
            for j in sorted_idxs:
                if j == i or j in removed:
                    continue
                mj = masks[j]
                inter = np.logical_and(mi, mj).sum()
                if inter / np.sum(mj) > iou_thresh:
                    removed.add(j)

        # Возвращаем итоговый массив масок
        return masks[keep]