# import queue
# import threading
# import cv2
# import numpy as np
# from ultralytics import YOLO
#
# from camera.detectors.YoloBoxDetector import YoloBoxDetector
#
# # ============================================
#
# video_url = 'http://192.168.137.72:4747/video'
# cap = cv2.VideoCapture(video_url)
# detector = YoloBoxDetector()
#
# # Очереди
# frame_queue = queue.Queue(maxsize=1)
# result_queue = queue.Queue(maxsize=1)
#
#
# # Обработка в фоне
# def process_frames():
#     while True:
#         frame = frame_queue.get()
#         if frame is None:
#             result_queue.put(None)
#             break
#         processed = detector.detect(frame)
#         result_queue.put(processed)
#
#
# processing_thread = threading.Thread(target=process_frames)
# processing_thread.start()
#
# if not cap.isOpened():
#     print("Ошибка: Не удалось подключиться к камере.")
# else:
#     while True:
#         # Получаем кадр
#         ret, frame = cap.read()
#         if not ret:
#             print("Ошибка: Не удалось получить кадр.")
#             break
#
#         # Передаём на обработку (если очередь пуста)
#         if frame_queue.empty():
#             frame_queue.put(frame)
#
#         # Отображаем результат
#         if not result_queue.empty():
#             processed = result_queue.get()
#             if processed is None:
#                 break
#             cv2.imshow("Phone Camera", processed)
#
#         # Обрабатываем события окна и выходим по 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
# # Завершаем
# cap.release()
# frame_queue.put(None)
# processing_thread.join()
# cv2.destroyAllWindows()
#
#
