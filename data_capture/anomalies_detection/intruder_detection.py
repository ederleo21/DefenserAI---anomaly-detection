import cv2
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')

prototxt_path = os.path.join(models_dir, "deploy.prototxt")
model_path = os.path.join(models_dir, "mobilenet_iter_73000.caffemodel")

net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

def detect_intruder(frame, results):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    intruder_detected = False
    confidence = 0.0

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            class_id = int(detections[0, 0, i, 1])
            if class_id == 15:
                intruder_detected = True
                results['intruder_detected'] = (intruder_detected, confidence)
                return

    results['intruder_detected'] = (intruder_detected, confidence)
