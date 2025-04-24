import cv2
import numpy as np
import os
from scipy.spatial import distance

current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')

prototxt_path = os.path.join(models_dir, "deploy.prototxt")
model_path = os.path.join(models_dir, "mobilenet_iter_73000.caffemodel")
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

CONFIDENCE_THRESHOLD = 0.8
AGGLOMERATION_THRESHOLD = 180 
PEOPLE_THRESHOLD = 8

def detect_agglomeration(frame, results):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    persons = [] 

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > CONFIDENCE_THRESHOLD:
            idx = int(detections[0, 0, i, 1])

            if idx == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                centerX, centerY = (startX + endX) // 2, (startY + endY) // 2
                persons.append((centerX, centerY))

    if len(persons) > 1:
        distances = distance.cdist(persons, persons, 'euclidean')
        close_groups = []
        avg_confidence = 0.0
        detected_groups = 0

        for i in range(len(persons)):
            group = [i]
            for j in range(i + 1, len(persons)):
                if distances[i, j] < AGGLOMERATION_THRESHOLD:
                    group.append(j)
            close_groups.append(group)

        for group in close_groups:
            if len(group) >= PEOPLE_THRESHOLD:
                detected_groups += 1
                avg_confidence += CONFIDENCE_THRESHOLD

        if detected_groups > 0:
            avg_confidence /= detected_groups
            results['agglomeration'] = (True, avg_confidence)
            return

    results['agglomeration'] = (False, 0.0)
