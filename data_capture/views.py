import cv2
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import json
import base64
import time
import threading
from management.models import Camera
import queue
from .signals import alert_created
from collections import deque
from django.views.decorators.csrf import csrf_exempt
from .anomalies_detection.crowd_detection import detect_agglomeration
from .anomalies_detection.fight_detection import detect_fight
from .anomalies_detection.fall_detection import detect_fall
from .anomalies_detection.fire_detection import detect_fire
from .anomalies_detection.intruder_detection import detect_intruder
from .anomalies_detection.run_detection import detect_running
from .anomalies_detection.jump_detection import detect_jumps
from .anomalies_detection.agression_detection import detect_agression

MAX_QUEUE_SIZE = 10
IMG_SIZE = (224, 224)
selected_anomalies = ["agglomeration", "fight_detected", "fire_detected"]

image_queue = queue.Queue()
is_processing = False
last_detection_message = ""
alert_cooldown = 300
last_alert_time = 0
frame_history = deque(maxlen=10)

def preprocess_frame(frame):
    resized_frame = cv2.resize(frame, IMG_SIZE)
    input_frame = np.expand_dims(resized_frame, axis=0).astype(np.float32) / 255.0
    return input_frame

def process_images(user):
    global is_processing, last_detection_message, selected_anomalies
    global last_alert_time, alert_cooldown, frame_history

    while True:
        frame = image_queue.get()  
        if frame is None:
            break

        results = {'agglomeration': (False, 0.0),
                    'fight_detected': (False, 0.0),
                    'fall_detected': (False, 0.0),
                    'fire_detected': (False, 0.0),
                    'intruder_detected': (False, 0.0),
                    'run_detected': (False, 0.0),
                    'jump_detected': (False, 0.0),
                    'agression_detected': (False, 0.0)}
        threads = []
  
        if "agglomeration" in selected_anomalies:
            threads.append(threading.Thread(target=detect_agglomeration, args=(frame, results)))
        if "fight_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_fight, args=(frame, results)))
        if "fall_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_fall, args=(frame, results)))
        if "fire_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_fire, args=(frame, results)))
        if "intruder_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_intruder, args=(frame, results)))
        if "run_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_running, args=(frame, results)))
        if "jump_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_jumps, args=(frame, results)))
        if "agression_detected" in selected_anomalies:
            threads.append(threading.Thread(target=detect_agression, args=(frame, results)))
 
        for thread in threads:
            thread.start()

        for thread in threads:  
            thread.join()

        has_anomaly = any(value[0] for value in results.values())
        frame_history.append(1 if has_anomaly else 0)
        anomaly_detection_count = sum(frame_history)

        detection_message = ""
        total_confidence = 0.0
        detected_count = 0

        for anomaly, (detected, confidence) in results.items():
            if detected:
                detected_count += 1
                total_confidence += confidence
                if anomaly == 'fire_detected':
                    detection_message = "¡Fuego detectado! "
                elif anomaly == 'agglomeration':
                    detection_message = "¡Aglomeración detectada! "
                elif anomaly == 'fight_detected':
                    detection_message = "¡Pelea detectada! "
                elif anomaly == 'fall_detected':
                    detection_message = "¡Caída detectada! "
                elif anomaly == 'intruder_detected':
                    detection_message = "¡Intruso detectado! "
                elif anomaly == 'run_detected':
                    detection_message = "¡Persona corriendo! "
                elif anomaly == 'jump_detected':
                    detection_message = "¡Salto brusco! "
                elif anomaly == 'agression_detected':
                    detection_message = "¡Agresión detectada! "

        average_confidence = (total_confidence / detected_count) * 100 if detected_count > 0 else 0.0
        last_detection_message = detection_message if detection_message else "Sin anomalías."
        print(detection_message)

        current_time = time.time()
        if anomaly_detection_count >= 2: 
            if(current_time - last_alert_time) >= alert_cooldown:
                success, encoded_image = cv2.imencode('.jpg', frame)
        
                if success:
                    alert_created.send(
                        sender=None,
                        anomaly_type=last_detection_message.strip(),
                        confidence=round(average_confidence, 2),
                        frame_image=encoded_image.tobytes(),
                        user=user
                    )
                    last_alert_time = current_time

        image_queue.task_done()


def start_processing_thread(user):
    global is_processing
    if not is_processing:
        is_processing = True
        threading.Thread(target=process_images, args=(user,), daemon=True).start()


@login_required(login_url='accounts:login')
@csrf_exempt
def detect_anomaly(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data['image']

            header, encoded = image_data.split(',', 1)
            img_data = np.frombuffer(base64.b64decode(encoded), dtype=np.uint8)
            frame = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

            start_processing_thread(request.user)

            if image_queue.qsize() < MAX_QUEUE_SIZE:
                image_queue.put(frame)
            
            return JsonResponse({'status': 'Image added to queue for processing.', 'detection_message': last_detection_message})

        except (ValueError, KeyError) as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='accounts:login')
def main(request):
    cameras = Camera.objects.all()
    start_trasmission = request.user.has_perm('management.start_trasmission')
    permissions = {
        'start_trasmission' : start_trasmission,
    }
    return render(request, "data_capture/main.html", {'cameras': cameras, 'permissions': permissions})

@csrf_exempt
@login_required(login_url='accounts:login')
def set_anomalies(request):
    global selected_anomalies
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_anomalies = data.get('selectedAnomalies', ["agglomeration", "fight_detected", "fall_detected", "fire_detected"])
        return JsonResponse({'status': 'Anomalías actualizadas correctamente.'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

