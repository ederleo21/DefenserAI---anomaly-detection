from django.urls import path
from .views import create_alert_and_send_email, alertt

app_name = 'alerts'

urlpatterns = [
    path('mail/', create_alert_and_send_email, name='mail'),
    path('alert/', alertt, name='alert'),
]

