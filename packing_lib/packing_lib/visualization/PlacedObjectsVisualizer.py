from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random

from packing_lib.packing_lib.types import PlacedObject, PackingContainer


class PlacedObjectsVisualizer:
    """Визуализатор результатов упаковки объектов"""
    
    def __init__(self, container: PackingContainer):
        self.container = container
        self._color_cache = {}
    
    def _get_color_for_id(self, obj_id: int) -> str:
        """Генерирует стабильный цвет для объекта по его ID"""
        if obj_id not in self._color_cache:
            rng = random.Random(obj_id)
            # Генерируем приятные цвета
            colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 
                     'lightpink', 'lightgray', 'lightyellow', 'lightcyan',
                     'plum', 'wheat', 'khaki', 'lavender']
            self._color_cache[obj_id] = rng.choice(colors)
        return self._color_cache[obj_id]
    
    def visualize(self, placed_objects: List[PlacedObject], 
                  title: str = "Packing Result",
                  show_metrics: bool = True,
                  show_grid: bool = True,
                  figsize: tuple = (10, 8)) -> None:
        """
        Визуализирует результат упаковки
        
        Args:
            placed_objects: Список размещенных объектов
            title: Заголовок графика
            show_metrics: Показывать метрики упаковки
            show_grid: Показывать сетку
            figsize: Размер фигуры
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Настройка осей
        ax.set_xlim(0, self.container.width)
        ax.set_ylim(0, self.container.height)
        ax.set_aspect('equal')
        
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        # Рисуем контейнер
        container_rect = patches.Rectangle(
            (0, 0),
            self.container.width,
            self.container.height,
            linewidth=2,
            edgecolor='black',
            facecolor='none'
        )
        ax.add_patch(container_rect)
        
        # Рисуем объекты
        for obj in placed_objects:
            color = self._get_color_for_id(obj.id)
            
            rect = patches.Rectangle(
                (obj.left, obj.top),  # используем свойства left/top
                obj.width,
                obj.height,
                linewidth=1,
                edgecolor='black',
                facecolor=color,
                alpha=0.7
            )
            ax.add_patch(rect)
            
            # Добавляем ID в центр объекта (центр уже известен)
            ax.text(obj.center_x, obj.center_y, str(obj.id),
                   ha='center', va='center', fontweight='bold',
                   fontsize=8, color='black')
        
        # Инвертируем Y-ось для соответствия пиксельным координатам
        ax.invert_yaxis()
        
        # Заголовок с метриками
        if show_metrics:
            metrics = self._calculate_metrics(placed_objects)
            title_with_metrics = f"{title}\n{metrics}"
        else:
            title_with_metrics = title
            
        ax.set_title(title_with_metrics, fontsize=12)
        ax.set_xlabel('Width (mm)', fontsize=10)
        ax.set_ylabel('Height (mm)', fontsize=10)
        
        plt.tight_layout()
        plt.show()
    
    def _calculate_metrics(self, placed_objects: List[PlacedObject]) -> str:
        """Вычисляет метрики упаковки"""
        if not placed_objects:
            return "Objects: 0, Density: 0%"
        
        total_object_area = sum(obj.width * obj.height for obj in placed_objects)
        container_area = self.container.width * self.container.height
        density = (total_object_area / container_area) * 100
        
        return f"Objects: {len(placed_objects)}, Density: {density:.1f}%"
    
    def save(self, placed_objects: List[PlacedObject], 
             filepath: str,
             title: str = "Packing Result",
             show_metrics: bool = True,
             show_grid: bool = True,
             figsize: tuple = (10, 8),
             dpi: int = 300) -> None:
        """
        Сохраняет визуализацию в файл
        
        Args:
            placed_objects: Список размещенных объектов
            filepath: Путь для сохранения
            title: Заголовок графика
            show_metrics: Показывать метрики упаковки
            show_grid: Показывать сетку
            figsize: Размер фигуры
            dpi: Разрешение изображения
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Тот же код отрисовки что и в visualize()
        ax.set_xlim(0, self.container.width)
        ax.set_ylim(0, self.container.height)
        ax.set_aspect('equal')
        
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        container_rect = patches.Rectangle(
            (0, 0),
            self.container.width,
            self.container.height,
            linewidth=2,
            edgecolor='black',
            facecolor='none'
        )
        ax.add_patch(container_rect)
        
        for obj in placed_objects:
            color = self._get_color_for_id(obj.id)
            
            rect = patches.Rectangle(
                (obj.left, obj.top),  # используем свойства left/top
                obj.width,
                obj.height,
                linewidth=1,
                edgecolor='black',
                facecolor=color,
                alpha=0.7
            )
            ax.add_patch(rect)
            
            # Добавляем ID в центр объекта (центр уже известен)
            ax.text(obj.center_x, obj.center_y, str(obj.id),
                   ha='center', va='center', fontweight='bold',
                   fontsize=8, color='black')
        
        ax.invert_yaxis()
        
        if show_metrics:
            metrics = self._calculate_metrics(placed_objects)
            title_with_metrics = f"{title}\n{metrics}"
        else:
            title_with_metrics = title
            
        ax.set_title(title_with_metrics, fontsize=12)
        ax.set_xlabel('Width (mm)', fontsize=10)
        ax.set_ylabel('Height (mm)', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close()