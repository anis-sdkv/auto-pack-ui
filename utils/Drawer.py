import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def draw_objects(data):
    box_width = data['box_width']
    box_height = data['box_height']

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, box_width)
    ax.set_ylim(0, box_height)
    ax.set_aspect('equal')

    for obj in data['objects']:
        rect = patches.Rectangle(
            (obj['x'], box_height - obj['y'] - obj['h']),
            obj['w'],
            obj['h'],
            linewidth=1,
            edgecolor='black',
            facecolor='skyblue',
            alpha=0.5
        )
        ax.add_patch(rect)

    ax.grid(True)
    ax.axis('off')
    plt.show()


def load_and_draw(dir_path):
    for filename in os.listdir(dir_path):
        with open(dir_path + filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        draw_objects(data)


# Запуск
if __name__ == "__main__":
    load_and_draw("../out/bench/dataset_test/phys/")
