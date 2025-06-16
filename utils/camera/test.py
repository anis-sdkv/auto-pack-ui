import cv2
import numpy as np

from utils.camera.calibration import scale_camera_matrix

# from utils.camera.calibration import scale_camera_matrix

CALIB_FILE = "calibration.npz"
STREAM_URL = "http://192.168.137.60:4747/video"

data = np.load(CALIB_FILE)
K = data["camera_matrix"]
dist = data["dist_coeffs"]

original_shape = (960, 1280)
new_shape = (480, 640)

K_scaled = scale_camera_matrix(K, original_shape, new_shape)

print("Loaded calibration matrix:")
print("K =", K)
print("dist =", dist.flatten())

cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("error")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("error")
        break

    undistorted = cv2.undistort(frame, K_scaled, dist)

    combined = np.hstack((frame, undistorted))
    combined_resized = cv2.resize(combined, (combined.shape[1] // 2, combined.shape[0] // 2))

    cv2.imshow("Original | Undistorted", combined_resized)

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
