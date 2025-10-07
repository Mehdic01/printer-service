import base64, threading, queue, time
from PIL import Image
from io import BytesIO
from .app_logger import log_event
from ..models import PrintJob

_job_q = queue.Queue()
_worker_started = False
_driver_provider = None   # connection_manager cm üzerinden set edilecek

def start_worker(driver_provider):
    global _worker_started, _driver_provider
    if _worker_started: return
    _driver_provider = driver_provider
    t = threading.Thread(target=_worker_loop, daemon=True)
    t.start()
    _worker_started = True

def enqueue(job: PrintJob):
    _job_q.put(job)

def _worker_loop():
    while True:
        job: PrintJob = _job_q.get()
        if not job: 
            time.sleep(0.1); 
            continue
        job.status = "running"; job.save()
        drv = _driver_provider()  # aktif driver
        op = f"print_{job.type}"
        try:
            if job.type == "text":
                drv.print_text(job.payload.get("text",""))
            elif job.type == "image":
                b64 = job.payload.get("base64","")
                img = Image.open(BytesIO(base64.b64decode(b64)))
                # Genişliği 384px'e sabitle (yaygın 80mm)
                target_w = int(job.payload.get("width", 384))
                w, h = img.size
                if w != target_w:
                    new_h = int(h * (target_w / float(w)))
                    img = img.resize((target_w, new_h))
                buf = BytesIO(); img.save(buf, format="PNG")
                drv.print_image(buf.getvalue())
            elif job.type == "qr":
                drv.print_qr(job.payload.get("data",""), size=job.payload.get("size",6))
            job.status = "ok"; job.error_code = None; job.save()
            log_event(op, job.conn_mode_snapshot, job.job_id, "ok")
        except Exception as e:
            code = getattr(e, "code", "UNKNOWN_COMMAND")
            detail = getattr(e, "detail", str(e))
            job.status = "error"; job.error_code = code; job.retries += 1; job.save()
            log_event(op, job.conn_mode_snapshot, job.job_id, "error",
                      error={"code": code, "detail": detail})
        finally:
            _job_q.task_done()
