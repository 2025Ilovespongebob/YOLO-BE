"""YOLO Detection Service"""
import os
from pathlib import Path
from ultralytics import YOLO
import numpy as np

# Model path
MODEL_PATH = Path(__file__).parent.parent / "best.pt"


class YOLOService:
    """YOLO model service for object detection"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load YOLO model"""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        self._model = YOLO(str(MODEL_PATH))
        print(f"✅ YOLO model loaded from {MODEL_PATH}")
    
    def detect(self, frame: np.ndarray, conf_threshold: float = 0.5):
        """
        Run detection on a frame
        
        Args:
            frame: numpy array (BGR image)
            conf_threshold: confidence threshold
            
        Returns:
            dict with detections and annotated frame
        """
        results = self._model(frame, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    detection = {
                        "class_id": int(box.cls[0]),
                        "class_name": self._model.names[int(box.cls[0])],
                        "confidence": float(box.conf[0]),
                        "bbox": {
                            "x1": float(box.xyxy[0][0]),
                            "y1": float(box.xyxy[0][1]),
                            "x2": float(box.xyxy[0][2]),
                            "y2": float(box.xyxy[0][3]),
                        }
                    }
                    detections.append(detection)
        
        # Get annotated frame
        annotated_frame = results[0].plot()
        
        return {
            "detections": detections,
            "annotated_frame": annotated_frame
        }
    
    def get_class_names(self):
        """Get model class names"""
        return self._model.names


# Singleton instance
yolo_service = YOLOService()
