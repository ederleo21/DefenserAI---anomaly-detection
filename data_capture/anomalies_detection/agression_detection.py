import cv2
import numpy as np
from scipy.spatial import distance
import mediapipe as mp
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')

prototxt_path = os.path.join(models_dir, "deploy.prototxt")
model_path = os.path.join(models_dir, "mobilenet_iter_73000.caffemodel")
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

CONFIDENCE_THRESHOLD = 0.7
DISTANCE_THRESHOLD = 250 
MOVEMENT_THRESHOLD = 15  
SPEED_THRESHOLD = 50  

prev_positions = {}
prev_time = {}

def detect_agression(frame, results):
    h, w, _ = frame.shape
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    persons = []
    bounding_boxes = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            idx = int(detections[0, 0, i, 1])
            if idx == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                centerX, centerY = (startX + endX) // 2, (startY + endY) // 2
                persons.append((centerX, centerY))
                bounding_boxes.append((startX, startY, endX, endY))

    if len(persons) >= 2:
        distances = distance.cdist(persons, persons, 'euclidean')
        for i in range(len(persons)):
            for j in range(len(persons)):
                if i != j and distances[i, j] < DISTANCE_THRESHOLD:
                    roi_i = frame[bounding_boxes[i][1]:bounding_boxes[i][3], bounding_boxes[i][0]:bounding_boxes[i][2]]
                    roi_j = frame[bounding_boxes[j][1]:bounding_boxes[j][3], bounding_boxes[j][0]:bounding_boxes[j][2]]
                    results_i = pose.process(cv2.cvtColor(roi_i, cv2.COLOR_BGR2RGB))
                    results_j = pose.process(cv2.cvtColor(roi_j, cv2.COLOR_BGR2RGB))

                    def get_pixel_coords(landmark, width, height):
                        return int(landmark.x * width), int(landmark.y * height)

                    if results_i.pose_landmarks and results_j.pose_landmarks:
                        landmarks_i = results_i.pose_landmarks.landmark
                        landmarks_j = results_j.pose_landmarks.landmark
                        elbow_left_i = get_pixel_coords(landmarks_i[mp_pose.PoseLandmark.LEFT_ELBOW.value], bounding_boxes[i][2] - bounding_boxes[i][0], bounding_boxes[i][3] - bounding_boxes[i][1])
                        wrist_left_i = get_pixel_coords(landmarks_i[mp_pose.PoseLandmark.LEFT_WRIST.value], bounding_boxes[i][2] - bounding_boxes[i][0], bounding_boxes[i][3] - bounding_boxes[i][1])
                        elbow_right_i = get_pixel_coords(landmarks_i[mp_pose.PoseLandmark.RIGHT_ELBOW.value], bounding_boxes[i][2] - bounding_boxes[i][0], bounding_boxes[i][3] - bounding_boxes[i][1])
                        wrist_right_i = get_pixel_coords(landmarks_i[mp_pose.PoseLandmark.RIGHT_WRIST.value], bounding_boxes[i][2] - bounding_boxes[i][0], bounding_boxes[i][3] - bounding_boxes[i][1])

                        current_time = time.time()
                        if (wrist_left_i[1] < elbow_left_i[1] and wrist_right_i[1] < elbow_right_i[1]):
                            current_positions_i = {
                                "elbow_left": elbow_left_i,
                                "elbow_right": elbow_right_i,
                                "wrist_left": wrist_left_i,
                                "wrist_right": wrist_right_i
                            }

                            if i in prev_positions and i in prev_time:
                                for part in current_positions_i:
                                    movement_i = distance.euclidean(prev_positions[i][part], current_positions_i[part])
                                    time_diff = current_time - prev_time[i]
                                    speed = movement_i / time_diff if time_diff > 0 else 0

                                    if movement_i > MOVEMENT_THRESHOLD and speed > SPEED_THRESHOLD:
                                        results['agression_detected'] = (True, 0.9)  

                            prev_positions[i] = current_positions_i
                            prev_time[i] = current_time

    if not results['agression_detected'][0]:
        results['agression_detected'] = (False, 0.0)



 



