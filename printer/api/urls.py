from django.urls import path
from .views import connect, status, print_text, print_image, print_qr, logs, reprint, health

urlpatterns = [
    path("connect", connect),
    path("status", status),
    path("print/text", print_text),
    path("print/image", print_image),
    path("print/qr", print_qr),
    path("logs", logs),
    path("reprint", reprint),
    path("health", health),
]
