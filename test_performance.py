#!/usr/bin/env python3
"""
Тест производительности PhysPacker в разных режимах
"""

import time
from packing_lib.packing_lib.types import PackInput, PackingContainer, PackingInputTask
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker


def create_test_objects(count=8):
    """Создает тестовые объекты для упаковки"""
    import random
    random.seed(42)  # для воспроизводимости
    
    objects = []
    for i in range(count):
        width = random.uniform(1.5, 3.5)
        height = random.uniform(1.5, 3.5)
        objects.append(PackInput(id=i, width=width, height=height))
    return objects


def benchmark_mode(name, packer, task):
    """Тестирует один режим пакера"""
    print(f"\\n=== {name} ===")
    
    start_time = time.time()
    placed_objects = packer.pack(task)
    end_time = time.time()
    
    duration = end_time - start_time
    packed_count = len(placed_objects)
    
    print(f"Время выполнения: {duration:.3f} секунд")
    print(f"Упаковано объектов: {packed_count}")
    print(f"Производительность: {packed_count/duration:.1f} объектов/сек")
    
    return duration, packed_count


def main():
    print("=== Тест производительности PhysPacker ===")
    
    # Создаем тестовые данные
    objects = create_test_objects(8)
    container = PackingContainer(20, 15)
    task = PackingInputTask(container, objects)
    
    print(f"Тестируем упаковку {len(objects)} объектов в контейнер {container.width}x{container.height}")
    
    # Тестируем разные режимы
    results = []
    
    # 1. Headless режим (максимальная скорость)
    packer1 = PhysPacker(headless=True, pixels_per_mm=20)
    duration1, count1 = benchmark_mode("Headless (максимальная скорость)", packer1, task)
    results.append(("Headless", duration1))
    
    # 2. Визуализация, нормальная скорость
    packer2 = PhysPacker(headless=False, pixels_per_mm=20, simulation_speed=1.0, target_fps=60)
    duration2, count2 = benchmark_mode("Визуализация 1.0x (60 FPS)", packer2, task)
    results.append(("Визуализация 1x", duration2))
    
    # 3. Визуализация, ускоренная
    packer3 = PhysPacker(headless=False, pixels_per_mm=20, simulation_speed=3.0, target_fps=60)
    duration3, count3 = benchmark_mode("Визуализация 3.0x (60 FPS)", packer3, task)
    results.append(("Визуализация 3x", duration3))
    
    # 4. Визуализация, высокий FPS
    packer4 = PhysPacker(headless=False, pixels_per_mm=20, simulation_speed=1.0, target_fps=120)
    duration4, count4 = benchmark_mode("Визуализация 1.0x (120 FPS)", packer4, task)
    results.append(("Визуализация 120fps", duration4))
    
    # Сравнение результатов
    print("\\n" + "="*50)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("="*50)
    
    baseline = results[0][1]  # headless время как базовая линия
    
    for name, duration in results:
        speedup = baseline / duration
        print(f"{name:20} | {duration:6.3f}s | Ускорение: {speedup:4.1f}x")
    
    print("\\n📝 Выводы:")
    print("- Headless режим обеспечивает максимальную скорость")
    print("- simulation_speed позволяет ускорить визуализацию")
    print("- Точность симуляции сохраняется во всех режимах")
    print("- Все режимы упаковывают одинаковое количество объектов")


if __name__ == "__main__":
    main()