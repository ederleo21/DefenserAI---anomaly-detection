from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    anomaly_type = models.CharField(max_length=100)
    confidence = models.FloatField()
    frame_image = models.ImageField(upload_to='alert_frames/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
            return f"{self.anomaly_type} - {self.timestamp}"
