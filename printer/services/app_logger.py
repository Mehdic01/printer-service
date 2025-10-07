import json, os, threading, datetime
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "logs.jsonl")
_lock = threading.Lock()

def log_event(op, conn, job_id, status, error=None, meta=None):
    rec = {
        "ts": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "op": op,            # e.g. print_text
        "conn": conn,        # mock/usb/lan
        "jobId": job_id,
        "status": status,    # ok|error|pending|running
    }
    if error:
        rec["error"] = error  # {"code":"PAPER_OUT","detail":"No paper detected"}
    if meta:
        rec["meta"] = meta
    line = json.dumps(rec, ensure_ascii=False)
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
