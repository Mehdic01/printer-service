from django.contrib import admin
from django.urls import include, path

#bu dosya projenin ana url dosyasi, burada api/ altinda printer.api.urls dosyasini include ediyoruz ve boylece api/ altindaki tum endpointler printer/api/urls.py dosyasinda tanimlanmis oluyor
#Django'nun sagladigi admin arayuzu icin de admin/ altinda admin.site.urls'u include ettim 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("printer.api.urls")),  # API aynı kalsın
    path("", ui_index, name="ui_index"),

    # HTMX partials & actions
    path("ui/status", ui_status_partial, name="ui_status"),
    path("ui/jobs", ui_jobs_partial, name="ui_jobs"),
    path("ui/connect", ui_connect, name="ui_connect"),
    path("ui/print-text", ui_print_text, name="ui_print_text"),
    path("ui/print-image", ui_print_image, name="ui_print_image"),
    path("ui/print-qr", ui_print_qr, name="ui_print_qr"),
    path("ui/reprint", ui_reprint, name="ui_reprint"),
]
