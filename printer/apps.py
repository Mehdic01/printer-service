from django.apps import AppConfig

class PrinterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "printer"

    def ready(self):
        from .services.job_queue import start_worker
        from .services.connection_manager import cm
        # driver_provider, her çağrıldığında aktif driver'ı döndürsün:
        start_worker(lambda: cm.driver())
