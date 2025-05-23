from django.apps import AppConfig


class DataCaptureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_capture'

    def ready(self):
        import data_capture.signals