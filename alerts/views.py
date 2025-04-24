from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.shortcuts import render
from defenserai import settings
from .models import Alert
from django.utils import timezone
import os
from data_capture.signals import alert_created
from django.dispatch import receiver
import time

@receiver(alert_created)
def create_alert_and_send_email(sender, anomaly_type, confidence, frame_image, user, **kwargs):
    alert = Alert.objects.create(
        anomaly_type=anomaly_type,
        confidence=confidence,
        created_by=user,
        timestamp = timezone.now()
    )
    
    if frame_image is not None:
        alert.frame_image = save_frame_image(frame_image) 
        alert.save() 

    send_email_alert(alert)


def send_email_alert(alert):
    user_emails = User.objects.values_list('email', flat=True)
    
    subject = f"Alerta: {alert.anomaly_type}"
    formatted_time = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"Se ha detectado una anomalía:\n\n"
        f"Tipo: {alert.anomaly_type}\n"
        f"Confianza: {alert.confidence}%\n"
        f"Fecha y hora: {formatted_time} UTC"
    )

    email = EmailMessage(subject, message, to=user_emails)
    email.from_email = settings.DEFAULT_FROM_EMAIL

    if alert.frame_image:  
        image_path = os.path.join(settings.MEDIA_ROOT, alert.frame_image.name)  
        if os.path.exists(image_path): 
            email.attach_file(image_path)  

    email.send(fail_silently=False)


def save_frame_image(frame_image):
    image_name = f'alert_image_{int(time.time())}.jpg'
    image_path = os.path.join(settings.MEDIA_ROOT, 'alert_frames', image_name)

    with open(image_path, 'wb') as f:
        f.write(frame_image)

    return os.path.normpath(os.path.join('alert_frames', image_name)).replace(os.sep, '/')


def alertt(request):
    alerts = Alert.objects.all()
    return render(request, 'alerts/alert_sent.html', {'alerts': alerts})
