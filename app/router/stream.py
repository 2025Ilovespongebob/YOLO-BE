"""Streaming Router for YOLO Detection"""
import asyncio
import base64
import json
from typing import Optional

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.service.yolo_service import yolo_service

router = APIRouter(prefix="/stream", tags=["stream"])


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time YOLO detection streaming.
    
    Client sends: base64 encoded image frames
    Server responds: detection results with annotated frame
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive frame from client
            data = await websocket.receive_text()
            
            try:
                payload = json.loads(data)
                frame_data = payload.get("frame", "")
                conf_threshold = payload.get("conf_threshold", 0.5)
                
                # Decode base64 image
                if "," in frame_data:
                    frame_data = frame_data.split(",")[1]
                
                img_bytes = base64.b64decode(frame_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    await websocket.send_json({"error": "Invalid image frame"})
                    continue
                
                # Run YOLO detection
                result = yolo_service.detect(frame, conf_threshold)
                
                # Encode annotated frame to base64
                _, buffer = cv2.imencode('.jpg', result["annotated_frame"], [cv2.IMWRITE_JPEG_QUALITY, 80])
                annotated_b64 = base64.b64encode(buffer).decode('utf-8')
                
                # Send response
                response = {
                    "detections": result["detections"],
                    "annotated_frame": f"data:image/jpeg;base64,{annotated_b64}",
                    "detection_count": len(result["detections"])
                }
                
                await websocket.send_json(response)
                
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/detect")
async def detect_image(image_base64: str, conf_threshold: float = Query(0.5, ge=0.0, le=1.0)):
    """
    HTTP endpoint for single image detection.
    
    Args:
        image_base64: Base64 encoded image
        conf_threshold: Confidence threshold (0.0-1.0)
    
    Returns:
        Detection results with annotated frame
    """
    try:
        # Decode base64 image
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        img_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Run YOLO detection
        result = yolo_service.detect(frame, conf_threshold)
        
        # Encode annotated frame to base64
        _, buffer = cv2.imencode('.jpg', result["annotated_frame"], [cv2.IMWRITE_JPEG_QUALITY, 85])
        annotated_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "detections": result["detections"],
            "annotated_frame": f"data:image/jpeg;base64,{annotated_b64}",
            "detection_count": len(result["detections"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes")
async def get_classes():
    """Get available detection classes"""
    return {"classes": yolo_service.get_class_names()}


def generate_camera_frames(camera_id: int = 0, conf_threshold: float = 0.5):
    """Generator for camera stream with YOLO detection"""
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run YOLO detection
            result = yolo_service.detect(frame, conf_threshold)
            annotated_frame = result["annotated_frame"]
            
            # Encode to JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()


@router.get("/camera")
async def camera_stream(camera_id: int = Query(0, ge=0), conf_threshold: float = Query(0.5, ge=0.0, le=1.0)):
    """
    MJPEG stream from camera with YOLO detection.
    
    Access via: http://localhost:8000/stream/camera
    """
    return StreamingResponse(
        generate_camera_frames(camera_id, conf_threshold),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
