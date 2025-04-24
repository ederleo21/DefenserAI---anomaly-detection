from django.urls import path
from .views import main, detect_anomaly, set_anomalies

app_name = 'data_capture'

urlpatterns = [
    path('main/', main, name='main'),
    path('detect-anomaly/', detect_anomaly, name='detect_anomaly'),
    path('set_anomalies/', set_anomalies, name='set_anomalies'),
]

