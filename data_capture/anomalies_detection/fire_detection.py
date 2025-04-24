import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

model = load_model('models/modelV3.h5') 

labels = ["cars_accidents", "fight", "fire", "normal"] 

def preprocess_frame(frame):
    resized_frame = cv2.resize(frame, (224, 224))  
    img_array = np.array(resized_frame, dtype=np.float32)
    img_array = preprocess_input(img_array) 
    img_array = np.expand_dims(img_array, axis=0)  
    return img_array

def detect_fire(frame, results):
    preprocessed_frame = preprocess_frame(frame)
    predictions = model.predict(preprocessed_frame)
    
    predicted_class_index = np.argmax(predictions[0])
    predicted_class_label = labels[predicted_class_index]
    confidence = predictions[0][predicted_class_index]

    fire_detected = predicted_class_label == "fire" and confidence > 0.97
    
    results['fire_detected'] = (fire_detected, confidence)
