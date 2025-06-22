#!/usr/bin/env python3
"""
Простой тест генератора инструкций для манипулятора
"""

from packing_lib.packing_lib.types import PackInput, PackingContainer, PackingInputTask
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker
from packing_lib.packing_lib.manipulation.ManipulatorInstructionGenerator import ManipulatorInstructionGenerator
import random


def create_test_detected_objects():
    """Создаем тестовые объекты 'детекции'"""
    detected = []
    for i in range(5):
        # Имитируем RectObject с данными детекции
        obj = type('RectObject', (), {
            'id': i,
            'center_mm': (random.uniform(20, 80), random.uniform(20, 80)),
            'angle_deg': random.choice([0, 30, 45, 90, 135, 180]),
            'width': random.uniform(2, 4),
            'height': random.uniform(2, 4),
            'z': random.uniform(60, 120)
        })()
        detected.append(obj)
    return detected


def main():
    print("=== Тест генератора инструкций для манипулятора ===\n")
    
    # 1. Создаем объекты для упаковки
    pack_objects = [
        PackInput(id=i, width=random.uniform(2, 4), height=random.uniform(2, 4))
        for i in range(5)
    ]
    
    # 2. Упаковываем объекты
    container = PackingContainer(20, 15)
    task = PackingInputTask(container, pack_objects)
    
    packer = PhysPacker(headless=True, pixels_per_mm=20)
    packed_objects = packer.pack(task)
    
    print(f"Упаковано объектов: {len(packed_objects)}")
    
    # 3. Создаем данные 'детекции'
    detected_objects = create_test_detected_objects()
    
    # 4. Генерируем инструкции
    container_world_pos = (150.0, 75.0)  # координаты контейнера в мм
    generator = ManipulatorInstructionGenerator(container_world_pos)
    
    instructions, unpacked_ids = generator.generate_instructions(detected_objects, packed_objects)
    
    # 5. Выводим результаты
    print(f"\\nСгенерировано инструкций: {len(instructions)}")
    print("\\n--- Примеры инструкций ---")
    
    for i, instr in enumerate(instructions[:3]):  # показываем первые 3
        print(f"\\nОбъект {instr.id}:")
        print(f"  Захват:    x={instr.input.x:.1f}, y={instr.input.y:.1f}, θ={instr.input.theta:.0f}°")
        print(f"  Размещение: x={instr.output.x:.1f}, y={instr.output.y:.1f}, θ={instr.output.theta:.0f}°")
    
    # 6. Информация о неупакованных объектах
    if unpacked_ids:
        print(f"\\nНеупакованные объекты (IDs): {unpacked_ids}")
    else:
        print("\\nВсе объекты успешно упакованы!")
    
    # 7. Сохраняем в JSON
    generator.save_to_json(instructions, unpacked_ids, "test_manipulator_instructions.json")
    print(f"\\nИнструкции сохранены в: test_manipulator_instructions.json")


if __name__ == "__main__":
    main()