import threading
import queue
from typing import List, Callable, Optional, Any
from enum import Enum

from packing_lib.packing_lib.types import PlacedObject, PackingInputTask


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class PackingTask:
    def __init__(self, task_id: str, name: str, packer_func: Callable, task_data: PackingInputTask):
        self.task_id = task_id
        self.name = name
        self.packer_func = packer_func
        self.task_data = task_data
        self.status = TaskStatus.PENDING
        self.result: Optional[List[PlacedObject]] = None
        self.error: Optional[str] = None
        self.cancel_event = threading.Event()


class PackingTaskManager:
    def __init__(self):
        self.current_task: Optional[PackingTask] = None
        self.result_queue = queue.Queue()
        self.status_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        
    def add_status_callback(self, callback: Callable):
        """Добавляет callback для уведомлений о смене статуса"""
        self.status_callbacks.append(callback)
        
    def add_completion_callback(self, callback: Callable):
        """Добавляет callback для уведомлений о завершении задачи"""
        self.completion_callbacks.append(callback)
    
    def start_task(self, task: PackingTask) -> bool:
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            return False
            
        self.current_task = task
        task.status = TaskStatus.RUNNING
        self._notify_status_change()
        
        thread = threading.Thread(target=self._execute_task, args=(task,))
        thread.daemon = True
        thread.start()
        
        return True
    
    def cancel_current_task(self):
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            self.current_task.cancel_event.set()
            self.current_task.status = TaskStatus.CANCELLED
            self._notify_status_change()
            self._notify_completion()
    
    def get_current_status(self) -> tuple:
        if self.current_task:
            return self.current_task.status, self.current_task.name
        return TaskStatus.PENDING, ""
    
    def check_results(self):
        try:
            while True:
                task = self.result_queue.get_nowait()
                self.current_task = task
                self._notify_completion()
        except queue.Empty:
            pass
    
    def _execute_task(self, task: PackingTask):
        try:
            if task.cancel_event.is_set():
                task.status = TaskStatus.CANCELLED
                self.result_queue.put(task)
                return
            
            result = task.packer_func(task.task_data, task.cancel_event)
            
            if task.cancel_event.is_set():
                task.status = TaskStatus.CANCELLED
            else:
                task.result = result
                task.status = TaskStatus.COMPLETED
                
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.ERROR
        
        self.result_queue.put(task)
    
    def _notify_status_change(self):
        for callback in self.status_callbacks:
            try:
                callback(self.current_task.status, self.current_task.name)
            except Exception as e:
                print(f"Ошибка в status callback: {e}")
    
    def _notify_completion(self):
        for callback in self.completion_callbacks:
            try:
                callback(self.current_task)
            except Exception as e:
                print(f"Ошибка в completion callback: {e}")