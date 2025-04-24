import cv2
from ultralytics import YOLO
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')
model_path = os.path.join(models_dir, 'yolov8s.pt')

model = YOLO(model_path)  

def detect_fall(frame, results):
    frame = cv2.resize(frame, (640, 480))
    detections = model.predict(frame, conf=0.5)

    fall_detected = False
    highest_confidence = 0.0
    threshold_factor = 1.5  

    for result in detections:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls.item())
            confidence = box.conf.item()
            
            if cls == 0: 
                width = x2 - x1
                height = y2 - y1

                if width > (height * threshold_factor):
                    fall_detected = True
                    highest_confidence = max(highest_confidence, confidence)

    results['fall_detected'] = (fall_detected, highest_confidence)
