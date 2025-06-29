from typing import Optional, List, Any
import numpy


class MainScreenState:
    """Состояние MainScreen, которое живет независимо от UI"""
    
    def __init__(self):
        # Состояние камеры
        self.cam_fixed: bool = False
        self.detected_boxes: List[Any] = []
        self.generated_boxes: List[Any] = []
        self.camera_frame: Optional[numpy.ndarray] = None

        self.camera_width: Optional[int] = None
        self.camera_resolution_ratio: float = 1.0

        self.storage_objects: List[Any] = []
        self.pending_physics_result: Optional[List[Any]] = None
        
        self.status_message: str = "Готов к упаковке"
    
    def save_camera_state(self, cam_fixed: bool, detected_boxes: List[Any], 
                         generated_boxes: List[Any], camera_frame: Optional[numpy.ndarray],
                         camera_width: Optional[int] = None, camera_resolution_ratio: float = 1.0):
        self.cam_fixed = cam_fixed
        self.detected_boxes = detected_boxes.copy() if detected_boxes else []
        self.generated_boxes = generated_boxes.copy() if generated_boxes else []
        self.camera_frame = camera_frame
        if camera_width is not None:
            self.camera_width = camera_width
            self.camera_resolution_ratio = camera_resolution_ratio
    
    def save_physics_result(self, result: List[Any]):
        self.pending_physics_result = result.copy() if result else []
    
    def apply_physics_result(self):
        if self.pending_physics_result:
            self.storage_objects = self.pending_physics_result.copy()
            self.status_message = f"Физическая упаковка завершена: {len(self.pending_physics_result)} объектов размещено"
            self.pending_physics_result = None
            return True
        return False
    
    def set_storage_objects(self, objects: List[Any]):
        self.storage_objects = objects.copy() if objects else []
    
    def set_camera_resolution(self, width: int, height: int):
        self.camera_width = width
        self.camera_resolution_ratio = height / width

    def clear_camera_state(self):
        self.cam_fixed = False
        self.detected_boxes = []
        self.camera_frame = None
        self.status_message = "Готов к упаковке"
    
    def get_status_for_camera_state(self) -> str:
        if self.cam_fixed and self.detected_boxes:
            return f"Готов к упаковке ({len(self.detected_boxes)} объектов распознано)"
        return "Готов к упаковке"


main_screen_state = MainScreenState()