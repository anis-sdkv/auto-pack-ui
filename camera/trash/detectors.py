# class ObjectronBoxDetector:
#     def __init__(self, model_name='Cup', max_objects=5, detection_conf=0.5, tracking_conf=0.99):
#         self.model_name = model_name
#         self.max_objects = max_objects
#
#         self.mp_obj = mp.solutions.objectron
#         self.mp_drawing = mp.solutions.drawing_utils
#
#         self.detector = self.mp_obj.Objectron(
#             static_image_mode=False,
#             max_num_objects=self.max_objects,
#             min_detection_confidence=detection_conf,
#             min_tracking_confidence=tracking_conf,
#             model_name=self.model_name
#         )
#
#     def detect(self, frame):
#         # MediaPipe expects RGB
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.detector.process(rgb)
#         print(results)
#
#         boxes = []
#         if results.detected_objects:
#             for obj in results.detected_objects:
#                 # Нарисовать грани и оси
#                 self.mp_drawing.draw_landmarks(
#                     frame, obj.landmarks_2d, self.mp_obj.BOX_CONNECTIONS)
#                 self.mp_drawing.draw_axis(
#                     frame, obj.rotation, obj.translation)
#
#                 # Сохранить 3D инфу (вращение, трансляция)
#                 boxes.append({
#                     "rotation": obj.rotation,
#                     "translation": obj.translation
#                 })
#
#         return frame, boxes
#
#     def release(self):
#         self.detector.close()
#
#
# class YoloBoxDetector:
#     def __init__(self, model_path="yolo11n-seg.pt", target_classes=None, conf_threshold=0.3):
#         self.model = YOLO(model_path)
#         self.target_classes = target_classes or ['suitcase', 'backpack', 'handbag', 'box']
#         self.conf_threshold = conf_threshold
#         self.class_names = self.model.names
#
#     def detect(self, frame):
#         results = self.model(frame)  # Получаем список результатов
#         if len(results) == 0:
#             return frame  # Ничего не найдено, возвращаем оригинал
#
#         result = results[0]  # Берём первый (и обычно единственный) результат
#         img = frame.copy()
#
#         if result.masks is None or result.masks.data is None:
#             return img  # Нет масок — возвращаем оригинал
#
#         masks = result.masks.data.cpu().numpy()  # (N, H, W)
#         num_masks = masks.shape[0]
#
#         # Генерируем случайные цвета для каждой маски
#         colors = [np.random.randint(0, 255, (3,), dtype=np.uint8) for _ in range(num_masks)]
#
#         for i in range(num_masks):
#             mask = masks[i]
#             color = colors[i]
#
#             # Создаём цветную маску
#             colored_mask = np.zeros_like(img, dtype=np.uint8)
#             for c in range(3):
#                 colored_mask[:, :, c] = mask * color[c]
#
#             # Накладываем полупрозрачную маску
#             img = cv2.addWeighted(img, 1.0, colored_mask, 0.5, 0)
#             rect, box = self.get_rotated_bbox_from_mask(mask)
#             cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
#         return img
#
#     def get_rotated_bbox_from_mask(self, mask):
#         contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         if not contours:
#             return None
#
#         cnt = max(contours, key=cv2.contourArea)  # Берём самый большой контур
#         rect = cv2.minAreaRect(cnt)  # ((cx, cy), (w, h), angle)
#         box = cv2.boxPoints(rect)
#         box = box.astype(int)
#         return rect, box
#
#     def release(self):
#         pass  # Ничего не нужно освобождать
#
# class BoxSegmentationDetector:
#     def __init__(self, model_id: str = "box-segmentation-jdd1s/1", api_key="0MwV5qxzGg7zP6ad2IxN"):
#         self.model = get_model(model_id=model_id, api_key=api_key)
#         self.box_annotator = sv.BoxAnnotator()
#         self.label_annotator = sv.LabelAnnotator()
#
#     def detect(self, image: np.ndarray) -> np.ndarray:
#         results = self.model.infer(image)[0]
#         detections = sv.Detections.from_inference(results)
#
#         annotated = self.box_annotator.annotate(scene=image.copy(), detections=detections)
#         annotated = self.label_annotator.annotate(scene=annotated, detections=detections)
#
#         return annotated
#
# def undistort_image(img, mtx, dist):
#     h, w = img.shape[:2]
#     newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
#     dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
#     # Обрезка
#     x, y, w, h = roi
#     dst = dst[y:y+h, x:x+w]
#     return dst
