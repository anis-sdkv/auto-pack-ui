# PackingLib

Библиотека двумерной ортогональной упаковки прямоугольных объектов.

## Обзор

PackingLib — это комплексная библиотека Python для решения задач 2D упаковки прямоугольников в контейнер. Она предоставляет множество алгоритмов упаковки, возможности детекции объектов и инструменты визуализации для реальных приложений, связанных с физическим манипулированием объектами и оптимизацией контейнеров.

## Возможности

- **Множественные алгоритмы упаковки**:
  - Физическая упаковка с реалистичной симуляцией (PhysPacker)
  - Точная оптимизация с использованием программирования ограничений (ExactORToolsPacker)  
  - Эвристика Next-Fit Decreasing Height (NFDHPacker)

- **Интеграция компьютерного зрения**:
  - Детекция ArUco маркеров для калибровки сцены
  - Детекция объектов на основе YOLO
  - Автоматическое преобразование системы координат

- **Инструменты визуализации**:
  - Рендеринг физической симуляции в реальном времени
  - Визуализация обработки сцены
  - Визуализация результатов упаковки с метриками

- **Поддержка манипулятора**:
  - Генерация инструкций для роботического манипулирования
  - Преобразование входных/выходных координат

## Установка

### Зависимости

Библиотека требует следующие пакеты:

```bash
pip install opencv-python>=4.8.0
pip install opencv-contrib-python>=4.8.0
pip install ultralytics>=8.0.0
pip install pymunk>=6.0.0
pip install pygame>=2.0.0
pip install numpy>=1.20.0
pip install matplotlib>=3.5.0
pip install scipy>=1.7.0
pip install ortools>=9.0.0
```

### Установка из исходников

```bash
cd packing_lib
pip install -e .
```

Это автоматически установит все необходимые зависимости.

## Быстрый старт

### Базовое использование

```python
from packing_lib.packing_lib.types import PackingContainer, PackInputObject, PackingInputTask
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.visualization.PlacedObjectsVisualizer import PlacedObjectsVisualizer

# Определяем контейнер
container = PackingContainer(width=380, height=220)  # в мм

# Определяем объекты для упаковки
objects = [
    PackInputObject(id=0, width=50, height=30),
    PackInputObject(id=1, width=40, height=25),
    PackInputObject(id=2, width=60, height=35),
]

# Создаем задачу упаковки
task = PackingInputTask(container=container, objects=objects)

# Выбираем алгоритм упаковки
packer = NFDHPacker()
placed_objects = packer.pack(task)

# Визуализируем результаты
visualizer = PlacedObjectsVisualizer(container)
visualizer.visualize(placed_objects, title="Результат упаковки")
```

### Пайплайн компьютерного зрения

```python
import cv2
from packing_lib.packing_lib.SceneProcessor import SceneProcessor
from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector
from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector
from packing_lib.packing_lib.visualization.SceneProcessVisualizer import SceneProcessVisualizer

# Загружаем изображение
frame = cv2.imread("scene_image.jpg")

# Инициализируем детекторы (требуется калибровка камеры)
aruco = ArucoBoxDetector(marker_size_mm=23, camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
yolo = YoloBoxDetector()

# Обрабатываем сцену
processor = SceneProcessor(aruco, yolo)
result = processor.process(frame)

# Визуализируем результаты детекции
visualizer = SceneProcessVisualizer()
visualized = visualizer.visualize(frame, result)
cv2.imshow("Детекция сцены", visualized)
cv2.waitKey(0)

# Конвертируем обнаруженные объекты во входные данные для упаковки
detected_objects = result.converted_objects
task = PackingInputTask(container, PackingInputTask.from_rect_objects(detected_objects))
```

### Физическая упаковка

```python
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker

# Визуализация в реальном времени (медленнее)
packer = PhysPacker(headless=False, simulation_speed=1.0)

# Быстрый режим без визуализации
packer = PhysPacker(headless=True)

# Ускоренная визуализация
packer = PhysPacker(headless=False, simulation_speed=0.3)

placed_objects = packer.pack(task)
```

### Точная оптимизация

```python
from packing_lib.packing_lib.packers.ExactORToolsPacker import ExactORToolsPacker

# С разрешенным поворотом
packer = ExactORToolsPacker(time_limit_seconds=300, allow_rotation=True)

# Только фиксированная ориентация
packer = ExactORToolsPacker(time_limit_seconds=60, allow_rotation=False)

placed_objects = packer.pack(task)
```

## Алгоритмы упаковки

### PhysPacker
Физическая симуляция упаковки с использованием физического движка Pymunk. Обеспечивает реалистичное размещение объектов с учетом гравитации, столкновений и стабильности.

**Возможности:**
- Реалистичная физическая симуляция
- Поворот и оседание объектов
- Детекция столкновений
- Оптимизация стабильности
- Поддержка визуализации в реальном времени

**Случаи использования:** Когда важен физический реализм, объекты могут поворачиваться, или важна стабильность.

### ExactORToolsPacker
Точное решение на основе программирования ограничений с использованием Google OR-Tools. Находит оптимальные решения для небольших экземпляров задач.

**Возможности:**
- Оптимальные решения (при нахождении)
- Поддержка поворотов
- Настраиваемые ограничения по времени
- Резервная оптимизация подмножеств

**Случаи использования:** Когда требуется оптимальность и размер задачи управляем (< 20 объектов).

### NFDHPacker
Эвристический алгоритм Next-Fit Decreasing Height. Быстрый алгоритм аппроксимации, подходящий для больших экземпляров задач.

**Возможности:**
- Очень быстрое выполнение
- Хорошие результаты аппроксимации
- Обработка больших наборов объектов
- Предсказуемая производительность

**Случаи использования:** Когда критична скорость или работа с большим количеством объектов.

## Компоненты компьютерного зрения

### Детекция ArUco
Обнаруживает ArUco маркеры для калибровки сцены и установления системы координат.

```python
from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector

detector = ArucoBoxDetector(
    marker_size_mm=23,
    camera_matrix=camera_matrix,
    dist_coeffs=dist_coeffs
)
```

### Детекция объектов YOLO
Использует Ultralytics YOLO для детекции объектов на сценах.

```python
from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector

detector = YoloBoxDetector()
```

## Визуализация

### Визуализация обработки сцены
Показывает обнаруженные объекты и ArUco маркеры с системами координат.

### Визуализация результатов упаковки
Отображает упакованные объекты в контейнере с метриками плотности и цветовой кодировкой.

### Рендеринг физической симуляции
Рендеринг физической симуляции в реальном времени на основе pygame.

## Пример использования

См. `packing_lib/example.py` для полного примера, который демонстрирует:

1. Загрузку изображения с объектами
2. Детекцию ArUco маркеров и объектов с помощью YOLO
3. Обработку сцены и преобразование координат
4. Запуск различных алгоритмов упаковки
5. Визуализацию результатов

Для запуска примера:

```bash
cd packing_lib/packing_lib
python example.py
```

**Примечание:** Пример требует:
- Матрицы калибровки камеры в `AppConfig`
- Входное изображение по пути `../../in/det2.jpg`
- Правильную настройку ArUco маркеров (3 маркера для системы координат)

## Справочник API

### Основные типы

- `PackingContainer`: Определяет размеры контейнера и отступы
- `PackInputObject`: Объект для упаковки (id, ширина, высота)
- `PlacedObject`: Упакованный объект с финальной позицией
- `PackingInputTask`: Полное определение задачи упаковки
- `RectObject`: Обнаруженный объект с информацией о позе

### Интерфейс упаковки

Все упаковщики реализуют интерфейс `BasePacker`:

```python
def pack(self, task: PackingInputTask) -> List[PlacedObject]:
    # Возвращает список успешно упакованных объектов
    pass
```

### Обработка сцены

```python
def process(self, image: np.ndarray) -> SceneProcessResult:
    # Обрабатывает изображение и возвращает обнаруженные объекты с преобразованием координат
    pass
```

## Конфигурация

### Настройки физического движка
Измените `PhysicsConfig` для параметров физической симуляции:
- Гравитация, затухание, итерации
- Свойства объектов (масса, трение, эластичность)
- Временные параметры симуляции и пороги стабильности

### Параметры детекции
- Размер ArUco маркеров и калибровка камеры
- Выбор модели YOLO и пороги уверенности
- Допуски обработки сцены

## Заметки о производительности

- **PhysPacker**: Медленнее, но наиболее реалистичный, масштабируется со сложностью симуляции
- **ExactORToolsPacker**: Экспоненциальная сложность, практичен для < 20 объектов
- **NFDHPacker**: Линейная сложность, эффективно обрабатывает 100+ объектов

## Требования

- Python 3.7+
- OpenCV с поддержкой ArUco
- Файлы модели YOLO (автоматически загружаются ultralytics)
- Данные калибровки камеры для реальных приложений

## Лицензия

[Добавьте информацию о лицензии здесь]

## Автор

Анис Садыков

## Участие в разработке

[Добавьте руководящие принципы участия здесь]