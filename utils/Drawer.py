import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import math


def draw_objects_on_axes(ax, data, title=None):
    box_width = data['box_width']
    box_height = data['box_height']

    ax.set_xlim(0, box_width)
    ax.set_ylim(0, box_height)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])

    for obj in data['objects']:
        rect = patches.Rectangle(
            (obj['x'], box_height - obj['y'] - obj['h']),  # инверсия Y
            obj['w'],
            obj['h'],
            linewidth=0.8,
            edgecolor='black',
            facecolor='skyblue',
            alpha=0.5
        )
        ax.add_patch(rect)

    if title:
        ax.set_title(title, fontsize=8)


def load_and_draw_grid(dir_path):
    files = sorted([f for f in os.listdir(dir_path) if f.endswith(".json")])
    num_files = len(files)
    cols = math.ceil(math.sqrt(num_files))
    rows = math.ceil(num_files / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    axes = axes.flatten() if num_files > 1 else [axes]

    for i, filename in enumerate(files):
        full_path = os.path.join(dir_path, filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        draw_objects_on_axes(axes[i], data, title=filename)

    # Отключаем пустые ячейки, если они есть
    for j in range(len(files), len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()


# Запуск
if __name__ == "__main__":
    load_and_draw_grid("../out/bench/dataset_test/greedy")


