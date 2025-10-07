from django.shortcuts import render
from uuid import uuid4
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.connection_manager import cm
from ..models import PrintJob

# bu post istegi ile yaziciya baglanilir
#********************************************************************************************************************
@api_view(["POST"])
def connect(request):
    payload = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
    mode = payload.pop("mode", "mock")
    data = cm.connect(mode=mode, **payload)
    return Response(data)

#bu get istegi ile yazicinin durumu sorgulanir
#********************************************************************************************************************
@api_view(["GET"])
def status(request):
    return Response(cm.status())

# ortak fonksiyon: yeni bir print job yaratir veya idempotency key ile ayni job'i bulur
#********************************************************************************************************************
def _create_or_get_job(_type, payload, idem_key):
    # idempotency: varsa aynı job'ı döndür
    if idem_key:
        found = PrintJob.objects.filter(idem_key=idem_key).first()
        if found:
            return found
    job = PrintJob.objects.create(
        job_id=uuid4().hex[:12],
        idem_key=idem_key,
        type=_type,
        payload=payload,
        conn_mode_snapshot=cm.mode,
        status="ok",  # v0: hemen ok; 2. adımda worker'a taşıyacağız
    )
    return job

# text, image, qr yazdırma istekleri için ayrı ayrı endpointler
#********************************************************************************************************************
@api_view(["POST"])
def print_text(request):
    idem = request.headers.get("Idempotency-Key")
    text = request.data.get("text", "")
    job = _create_or_get_job("text", {"text": text}, idem)
    return Response({"jobId": job.job_id, "status": job.status}, status=202)

@api_view(["POST"])
def print_image(request):
    idem = request.headers.get("Idempotency-Key")
    base64s = request.data.get("base64", "")
    width = request.data.get("width", 384)
    job = _create_or_get_job("image", {"base64": base64s, "width": width}, idem)
    return Response({"jobId": job.job_id, "status": job.status}, status=202)

@api_view(["POST"])
def print_qr(request):
    idem = request.headers.get("Idempotency-Key")
    data = request.data.get("data", "")
    size = request.data.get("size", 6)
    job = _create_or_get_job("qr", {"data": data, "size": size}, idem)
    return Response({"jobId": job.job_id, "status": job.status}, status=202)

# logları listeleme, en son 100 kayıt
#********************************************************************************************************************
@api_view(["GET"])
def logs(request):
    qs = PrintJob.objects.order_by("-created_at")[:100]
    items = []
    for j in qs:
        items.append({
            "ts": j.created_at.isoformat(),
            "op": f"print_{j.type}",
            "conn": j.conn_mode_snapshot,
            "jobId": j.job_id,
            "status": j.status,
            "error": {"code": j.error_code} if j.error_code else None,
        })
    return Response(items)

# varolan bir job'i yeniden yazdırma (reprint)
#********************************************************************************************************************
@api_view(["POST"])
def reprint(request):
    job_id = request.data.get("jobId")
    src = PrintJob.objects.filter(job_id=job_id).first()
    if not src:
        return Response({"error": "not_found"}, status=404)
    new = PrintJob.objects.create(
        job_id=uuid4().hex[:12],
        type=src.type,
        payload=src.payload,
        status="ok",
        conn_mode_snapshot=cm.mode,
    )
    return Response({"jobId": new.job_id, "status": new.status}, status=202)

# sağlık kontrolü endpointi
#********************************************************************************************************************
@api_view(["GET"])
def health(request):
    return Response({"ok": True})
