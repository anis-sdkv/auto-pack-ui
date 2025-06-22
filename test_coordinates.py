#!/usr/bin/env python3
"""
Тест новой системы координат (центр объекта)
"""

from packing_lib.packing_lib.types import PackInput, PackingContainer, PackingInputTask, PlacedObject
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.visualization.PlacedObjectsVisualizer import PlacedObjectsVisualizer


def test_coordinate_system():
    print("=== Тест новой системы координат ===\n")
    
    # Создаем простые объекты
    objects = [
        PackInput(id=1, width=4, height=2),
        PackInput(id=2, width=3, height=3),
        PackInput(id=3, width=2, height=4)
    ]
    
    container = PackingContainer(10, 8)
    task = PackingInputTask(container, objects)
    
    # Упаковываем (используем NFDHPacker для детерминированного результата)
    packer = NFDHPacker()
    placed = packer.pack(task)
    
    print(f"Упаковано {len(placed)} объектов:")
    print()
    
    for obj in placed:
        print(f"Объект {obj.id}:")
        print(f"  Центр: ({obj.center_x:.1f}, {obj.center_y:.1f})")
        print(f"  Границы: left={obj.left:.1f}, top={obj.top:.1f}, right={obj.right:.1f}, bottom={obj.bottom:.1f}")
        print(f"  Размеры: {obj.width}x{obj.height}")
        print(f"  Старые свойства (deprecated): x={obj.x:.1f}, y={obj.y:.1f}")
        print()
    
    # Визуализируем результат
    print("Создание визуализации...")
    visualizer = PlacedObjectsVisualizer(container)
    visualizer.save(placed, "test_coordinates_result.png", title="Test: Center-based Coordinates")
    print("Визуализация сохранена в: test_coordinates_result.png")
    
    # Проверяем корректность
    print("\\n=== Проверка корректности ===")
    
    for obj in placed:
        # Проверяем что центр действительно в центре
        expected_center_x = (obj.left + obj.right) / 2
        expected_center_y = (obj.top + obj.bottom) / 2
        
        assert abs(obj.center_x - expected_center_x) < 0.001, f"Ошибка center_x для объекта {obj.id}"
        assert abs(obj.center_y - expected_center_y) < 0.001, f"Ошибка center_y для объекта {obj.id}"
        
        print(f"✓ Объект {obj.id}: координаты корректны")
    
    print("\\n✅ Все проверки пройдены!")


if __name__ == "__main__":
    test_coordinate_system()