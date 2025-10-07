import base64, threading, queue, time, os, random
from PIL import Image
from io import BytesIO
from .app_logger import log_event
from ..models import PrintJob
import environ

_job_q = queue.Queue()
_worker_started = False
_driver_provider = None   # connection_manager cm üzerinden set edilecek


#bu sinifin amaci yazici islemlerini arka planda yapabilmek
#yani job_queue modulu ile yazdirma islemi asenkron hale getiriliyor
#bunun icin bir thread baslatiliyor ve bu thread job_queue'dan isleri alip yaziciya gonderiyor
#boylece ana thread (api/views.py) yazdirma islemi ile ugrasmiyor ve daha hizli cevap verebiliyor
#ayrica yazdirma islemi basarisiz olursa job'un status'u error olarak guncelleniyor ve hata kodu kaydediliyor
#ayni zamanda retry mekanizmasi da var, yani yazdirma islemi basarisiz olursa belirli araliklarla tekrar deneniyor
#bunun icin settings.py'de RETRY_MAX, RETRY_BASE_MS, RETRY_JITTER_MS degiskenleri tanimlandi
#Bu tasarımda hata olduğunda job pending’e çekilir ve giderek artan gecikmelerle yeniden denenir 
# (örn. 0.8s → 1.6s → 3.2s). Jitter çakışmaları azaltır. Deneme sayısı retries alanında tutulur ve log’a yazılır.
#********************************************************************************************************************

# Environment variables
env = environ.Env(
    RETRY_BASE_MS=(int, 800),
    RETRY_MAX_ATTEMPTS=(int, 5),
    RETRY_JITTER_MS=(int, 200),
)
# .env dosyasını projenin kök dizininde arar
environ.Env.read_env(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

RETRY_BASE_MS = env("RETRY_BASE_MS")
RETRY_MAX = env("RETRY_MAX_ATTEMPTS")
RETRY_JITTER_MS = env("RETRY_JITTER_MS")


def start_worker(driver_provider):
    global _worker_started, _driver_provider
    if _worker_started: return
    _driver_provider = driver_provider
    t = threading.Thread(target=_worker_loop, daemon=True)
    t.start()
    _worker_started = True

def enqueue(job: PrintJob, delay_ms: int = 0):
    if delay_ms <= 0:
        _job_q.put(job)
    else:
        # gecikmeli tekrar kuyruğa at
        threading.Timer(delay_ms / 1000.0, lambda: _job_q.put(job)).start()


def _exp_backoff_delay_ms(retries_done: int) -> int:
    # ör.: 0→base, 1→2*base, 2→4*base + jitter
    base = RETRY_BASE_MS * (2 ** retries_done)
    jitter = random.randint(-RETRY_JITTER_MS, RETRY_JITTER_MS)
    return max(0, base + jitter)

def _worker_loop():
    while True:
        job: PrintJob = _job_q.get()
        if not job:
            time.sleep(0.05)
            continue

        job.status = "running"; job.save()
        drv = _driver_provider()
        op = f"print_{job.type}"

        try:
            if job.type == "text":
                text = job.payload.get("text", "")
                lang = job.payload.get("lang", "tr") 
                if lang == "en":
                    prefix = "\x1b\x52\x01"  # İngilizce karakter seti
                else:
                    prefix = "\x1b\x52\x00"  # Türkçe karakter seti
                    
                drv.print_text(text, prefix=prefix)
            elif job.type == "image":
                b64 = job.payload.get("base64","")
                img = Image.open(BytesIO(base64.b64decode(b64)))
                target_w = int(job.payload.get("width", 384))
                if img.size[0] != target_w:
                    new_h = int(img.size[1] * (target_w / float(img.size[0])))
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
            job.error_code = code
            job.retries += 1
            log_event(op, job.conn_mode_snapshot, job.job_id, "error",
                      error={"code": code, "detail": detail},
                      meta={"retries": job.retries})

            if job.retries <= RETRY_MAX:
                # backoff ile tekrar dene
                job.status = "pending"; job.save()
                delay = _exp_backoff_delay_ms(job.retries - 1)
                enqueue(job, delay_ms=delay)
            else:
                job.status = "error"; job.save()
        finally:
            _job_q.task_done()
