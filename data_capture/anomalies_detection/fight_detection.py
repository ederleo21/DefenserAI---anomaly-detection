import cv2
import numpy as np
from scipy.spatial import distance
import mediapipe as mp
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = os.path.join(os.path.dirname(current_dir), '..', 'models')

prototxt_path = os.path.join(models_dir, "deploy.prototxt")
model_path = os.path.join(models_dir, "mobilenet_iter_73000.caffemodel")
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

CONFIDENCE_THRESHOLD = 0.5
DISTANCE_THRESHOLD = 250
MOVEMENT_THRESHOLD = 12

prev_positions = {}  

def detect_fight(frame, results):
    global prev_positions 

    h, w, _ = frame.shape
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    persons = []  
    bounding_boxes = [] 

    highest_confidence = 0.0 
    fight_detected = False 

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

                highest_confidence = max(highest_confidence, confidence)

    if len(persons) > 1:
        distances = distance.cdist(persons, persons, 'euclidean')

        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                if distances[i, j] < DISTANCE_THRESHOLD: 
                    roi_i = frame[bounding_boxes[i][1]:bounding_boxes[i][3], bounding_boxes[i][0]:bounding_boxes[i][2]]
                    roi_j = frame[bounding_boxes[j][1]:bounding_boxes[j][3], bounding_boxes[j][0]:bounding_boxes[j][2]]

                    if roi_i.size == 0 or roi_j.size == 0:
                        continue 

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

                        elbow_left_j = get_pixel_coords(landmarks_j[mp_pose.PoseLandmark.LEFT_ELBOW.value], bounding_boxes[j][2] - bounding_boxes[j][0], bounding_boxes[j][3] - bounding_boxes[j][1])
                        wrist_left_j = get_pixel_coords(landmarks_j[mp_pose.PoseLandmark.LEFT_WRIST.value], bounding_boxes[j][2] - bounding_boxes[j][0], bounding_boxes[j][3] - bounding_boxes[j][1])
                        elbow_right_j = get_pixel_coords(landmarks_j[mp_pose.PoseLandmark.RIGHT_ELBOW.value], bounding_boxes[j][2] - bounding_boxes[j][0], bounding_boxes[j][3] - bounding_boxes[j][1])
                        wrist_right_j = get_pixel_coords(landmarks_j[mp_pose.PoseLandmark.RIGHT_WRIST.value], bounding_boxes[j][2] - bounding_boxes[j][0], bounding_boxes[j][3] - bounding_boxes[j][1])

                        if (wrist_left_i[1] < elbow_left_i[1] and wrist_right_i[1] < elbow_right_i[1] and 
                            wrist_left_j[1] < elbow_left_j[1] and wrist_right_j[1] < elbow_right_j[1]):
                            current_positions_i = {
                                "elbow_left": elbow_left_i,
                                "elbow_right": elbow_right_i,
                                "wrist_left": wrist_left_i,
                                "wrist_right": wrist_right_i
                            }
                            current_positions_j = {
                                "elbow_left": elbow_left_j,
                                "elbow_right": elbow_right_j,
                                "wrist_left": wrist_left_j,
                                "wrist_right": wrist_right_j
                            }

                            if i in prev_positions and j in prev_positions:
                                for part in current_positions_i:
                                    movement_i = distance.euclidean(prev_positions[i][part], current_positions_i[part])
                                    movement_j = distance.euclidean(prev_positions[j][part], current_positions_j[part])

                                    if movement_i > MOVEMENT_THRESHOLD and movement_j > MOVEMENT_THRESHOLD:
                                        fight_detected = True

                            prev_positions[i] = current_positions_i
                            prev_positions[j] = current_positions_j

    results['fight_detected'] = (fight_detected, highest_confidence)
    return
