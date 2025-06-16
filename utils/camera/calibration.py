import os

import cv2
import numpy as np
import glob

def scale_camera_matrix(K, original_shape, new_shape):
    h0, w0 = original_shape[:2]
    h1, w1 = new_shape[:2]

    scale_x = w1 / w0
    scale_y = h1 / h0

    K_scaled = K.copy()
    K_scaled[0, 0] *= scale_x   # fx
    K_scaled[1, 1] *= scale_y   # fy
    K_scaled[0, 2] *= scale_x   # cx
    K_scaled[1, 2] *= scale_y   # cy

    return K_scaled

# параметры шаблона
CHECKERBOARD = (9, 6)
square_size = 40.0  # мм

# подготовка объектов (в реальных координатах)
objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * square_size

objpoints = []  # 3D точки в мире
imgpoints = []  # 2D точки на изображении

images = glob.glob('calib_images/*.jpg')

output_dir = "output_chessboard"
os.makedirs(output_dir, exist_ok=True)

for f in os.listdir(output_dir):
    file_path = os.path.join(output_dir, f)
    if os.path.isfile(file_path):
        os.remove(file_path)

for i, fname in enumerate(images):
    img = cv2.imread(fname)
    print(img.shape)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # рисуем и сохраняем
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)
        output_path = os.path.join(output_dir, f"frame_{i:02d}.jpg")
        cv2.imwrite(output_path, img)
        cv2.imshow('Chessboard', img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

# калибровка
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# сохранить
np.savez("calibration.npz", camera_matrix=K, dist_coeffs=dist)
print("camera_matrix:\n", K)
print("distortion coefficients:\n", dist)
