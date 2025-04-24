from django.db import models
from django.db import models


class Report(models.Model):
    name = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='reports/')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reporte: {self.name} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"
