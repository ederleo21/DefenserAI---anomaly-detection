import cv2
import numpy as np
from ..tracking.sort import Sort 
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')

prototxt_path = os.path.join(models_dir, "deploy.prototxt")
model_path = os.path.join(models_dir, "mobilenet_iter_73000.caffemodel")
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

tracker = Sort()
CONFIDENCE_THRESHOLD = 0.5 
JUMP_THRESHOLD = 15 
JUMP_DETECTED_TIME = 0 
jump_detected = {}
previous_head_y_positions = {}

def detect_jumps(frame, results):
    global jump_detected, previous_head_y_positions

    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    dets = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            idx = int(detections[0, 0, i, 1])
            if idx == 15:  
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                dets.append([startX, startY, endX, endY, confidence])

    dets = np.array(dets)
    if dets.size > 0:
        tracks = tracker.update(dets)

        for track in tracks:
            track_id = int(track[4])
            startX, startY, endX, endY = map(int, track[:4])

            current_head_y = startY

            if track_id not in previous_head_y_positions:
                previous_head_y_positions[track_id] = current_head_y
                jump_detected[track_id] = 0
                continue

            height_difference = previous_head_y_positions[track_id] - current_head_y
            
            if abs(height_difference) > JUMP_THRESHOLD and jump_detected[track_id] == 0:
                results['jump_detected'] = (True, 1.0) 
                jump_detected[track_id] = JUMP_DETECTED_TIME

            if jump_detected[track_id] > 0:
                jump_detected[track_id] -= 1

            previous_head_y_positions[track_id] = current_head_y
