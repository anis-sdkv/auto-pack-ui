import cv2
import numpy as np
from scipy.ndimage import label


def binarize_image(image, white_threshold=240):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, white_threshold, 255, cv2.THRESH_BINARY)
    return binary // 255  # 1 for white, 0 for other


def find_connected_components(binary_mask):
    labeled_array, num_features = label(binary_mask)
    return labeled_array, num_features


def find_cut_lines(region_mask):
    rows, cols = region_mask.shape
    h_cuts = [0]
    for r in range(1, rows):
        if not np.array_equal(region_mask[r], region_mask[r - 1]):
            h_cuts.append(r)
    h_cuts.append(rows)

    v_cuts = [0]
    for c in range(1, cols):
        if not np.array_equal(region_mask[:, c], region_mask[:, c - 1]):
            v_cuts.append(c)
    v_cuts.append(cols)

    return h_cuts, v_cuts

def find_max_rectangle_from_point(mask, start_y, start_x):
    max_height = mask.shape[0]
    max_width = mask.shape[1]
    max_area = 0
    best_rect = None

    min_width = max_width
    for dy in range(start_y, max_height):
        if mask[dy, start_x] == 0:
            break
        row_width = 0
        for dx in range(start_x, max_width):
            if mask[dy, dx] == 1:
                row_width += 1
            else:
                break
        min_width = min(min_width, row_width)
        area = min_width * (dy - start_y + 1)
        if area > max_area:
            max_area = area
            best_rect = (start_x, start_y, min_width, dy - start_y + 1)

    return best_rect, max_area


def extract_rectangles_from_region(region_mask, top_left):
    mask = region_mask.copy()
    max_rectangles = []

    visited = np.zeros_like(mask, dtype=bool)
    rows, cols = mask.shape

    for y in range(rows):
        for x in range(cols):
            if mask[y, x] == 1 and not visited[y, x]:
                rect, area = find_max_rectangle_from_point(mask, y, x)
                if rect:
                    rx, ry, w, h = rect
                    # Пометить как пройдено
                    mask[ry:ry + h, rx:rx + w] = 0
                    visited[ry:ry + h, rx:rx + w] = True
                    max_rectangles.append((
                        top_left[1] + rx,
                        top_left[0] + ry,
                        w,
                        h
                    ))
    return max_rectangles


def find_empty_areas(image):
    binary_mask = binarize_image(image)
    labeled, num = find_connected_components(binary_mask)
    rectangles = []

    for label_idx in range(1, num + 1):
        region_mask = (labeled == label_idx).astype(np.uint8)
        ys, xs = np.where(region_mask)
        top, bottom, left, right = np.min(ys), np.max(ys), np.min(xs), np.max(xs)
        sub_mask = region_mask[top:bottom + 1, left:right + 1]
        rects = extract_rectangles_from_region(sub_mask, (top, left))
        rectangles.extend(rects)

    return rectangles
