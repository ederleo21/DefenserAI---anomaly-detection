from django.db import models


class Camera(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        permissions = [
            ("start_trasmission", "Can start trasmission"),
        ]

    def __str__(self):
        return self.name
