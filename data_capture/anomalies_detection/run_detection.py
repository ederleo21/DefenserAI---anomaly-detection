import cv2
import numpy as np
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')

prototxt_path = os.path.join(models_dir, "deploy.prototxt")
model_path = os.path.join(models_dir, "mobilenet_iter_73000.caffemodel")
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

CONFIDENCE_THRESHOLD = 0.7
VELOCITY_THRESHOLD = 160  

previous_positions = {}

def detect_running(frame, results):
    global previous_positions
    
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    results['run_detected'] = (False, 0.0)
    current_positions = {}

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            idx = int(detections[0, 0, i, 1])
            if idx == 15: 
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                centerX, centerY = (startX + endX) // 2, (startY + endY) // 2

                current_positions[i] = (centerX, centerY)
                if i in previous_positions:
                    prevX, prevY = previous_positions[i]
                    distance = np.sqrt((centerX - prevX) ** 2 + (centerY - prevY) ** 2)

                    if distance > VELOCITY_THRESHOLD:
                        results['run_detected'] = (True, distance) 
                        break  
                previous_positions[i] = (centerX, centerY)
                
    previous_positions = current_positions
    return results['run_detected']
