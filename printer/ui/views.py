from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from uuid import uuid4
from ..services.connection_manager import cm
from ..services.job_queue import enqueue
from ..models import PrintJob

# ------- Helpers -------
def create_job(_type, payload, idem_key=None):
    # UI'de idem_key zorunlu değil ama istersen ekleyebilirsin
    job = PrintJob.objects.create(
        job_id=uuid4().hex[:12],
        idem_key=idem_key,
        type=_type,
        payload=payload,
        status="pending",
        conn_mode_snapshot=cm.mode,
    )
    enqueue(job)
    return job

# ------- Pages / Partials -------
def ui_index(request):
    # Ana sayfa (HTMX ile status & jobs yüklenir)
    return render(request, "index.html", {})

def ui_status_partial(request):
    s = cm.status()
    return render(request, "partials/status.html", {"s": s})

def ui_jobs_partial(request):
    jobs = PrintJob.objects.order_by("-created_at")[:20]
    return render(request, "partials/jobs.html", {"jobs": jobs})

# ------- Actions -------
@require_http_methods(["POST"])
def ui_connect(request):
    mode = request.POST.get("mode", "mock")
    cm.connect(mode)
    # Bağlantı sonrası status panelini tazelemek için partial dönüyoruz
    s = cm.status()
    return render(request, "partials/status.html", {"s": s})

@require_http_methods(["POST"])
def ui_print_text(request):
    text = request.POST.get("text", "")
    if not text.strip():
        return HttpResponse("<div class='text-red-600'>Metin boş olamaz.</div>")
    job = create_job("text", {"text": text})
    # İşlem sonrası jobs panelini tazele
    jobs = PrintJob.objects.order_by("-created_at")[:20]
    return render(request, "partials/jobs.html", {"jobs": jobs})

@require_http_methods(["POST"])
def ui_print_image(request):
    # Basit kullanım: textarea'ya base64 yapıştırıp yollarız (demo yeterli)
    b64 = request.POST.get("base64", "")
    width = int(request.POST.get("width", "384"))
    if not b64:
        return HttpResponse("<div class='text-red-600'>Base64 görsel gerekli.</div>")
    job = create_job("image", {"base64": b64, "width": width})
    jobs = PrintJob.objects.order_by("-created_at")[:20]
    return render(request, "partials/jobs.html", {"jobs": jobs})

@require_http_methods(["POST"])
def ui_print_qr(request):
    data = request.POST.get("data", "")
    size = int(request.POST.get("size", "6"))
    if not data:
        return HttpResponse("<div class='text-red-600'>QR verisi gerekli.</div>")
    job = create_job("qr", {"data": data, "size": size})
    jobs = PrintJob.objects.order_by("-created_at")[:20]
    return render(request, "partials/jobs.html", {"jobs": jobs})

@require_http_methods(["POST"])
def ui_reprint(request):
    job_id = request.POST.get("jobId")
    src = PrintJob.objects.filter(job_id=job_id).first()
    if not src:
        return HttpResponse("<div class='text-red-600'>Kayıt bulunamadı.</div>")
    new = create_job(src.type, src.payload)
    jobs = PrintJob.objects.order_by("-created_at")[:20]
    return render(request, "partials/jobs.html", {"jobs": jobs})
