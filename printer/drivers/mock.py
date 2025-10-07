import random
from dataclasses import dataclass

class PrinterError(Exception):
    def __init__(self, code, detail=""):
        super().__init__(detail)
        self.code = code
        self.detail = detail

@dataclass
class MockState:
    paper_ok: bool = True
    cover_closed: bool = True
    overheat: bool = False

class MockDriver:
    def __init__(self):
        self.state = MockState()
        self.mode = "mock"

    def connect(self, **kwargs):
        # always ok for mock
        return True

    def status(self):
        return {
            "paper": "ok" if self.state.paper_ok else "out",
            "cover": "closed" if self.state.cover_closed else "open",
            "overheat": self.state.overheat,
        }

    def _maybe_error(self):
        # basit hata simülasyonu: %5 kağıt, %2 kapak
        r = random.random()
        if not self.state.paper_ok or r < 0.05:
            self.state.paper_ok = False
            raise PrinterError("PAPER_OUT", "No paper detected")
        if not self.state.cover_closed or r < 0.02:
            self.state.cover_closed = False
            raise PrinterError("COVER_OPEN", "Cover is open")

    def print_text(self, text, **kwargs):
        self._maybe_error()
        return True

    def print_image(self, img_bytes, **kwargs):
        self._maybe_error()
        return True

    def print_qr(self, data, **kwargs):
        self._maybe_error()
        return True

    # UI'dan “kağıt taktım/kapattım” simülasyonu için yardımcılar istersek:
    def fix_paper(self): self.state.paper_ok = True
    def close_cover(self): self.state.cover_closed = True
