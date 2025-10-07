from ..drivers.mock import MockDriver

# BU DOSYA SADECE TEK BİR CONNECTION MANAGER İÇERİR
# Singleton pattern ile tek instance sağlanır
class ConnectionManager:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.mode = "mock"
            cls._instance.connected = False
            cls._instance.last_error = None
            cls._instance._driver = MockDriver()
        return cls._instance

    def connect(self, mode="mock", **kwargs):
        # Şimdilik mock; ileride mode'a göre USB/LAN sürücü atanır
        self.mode = "mock" if mode not in ("usb","lan","mock") else mode
        self.connected = self._driver.connect(**kwargs)
        self.last_error = None
        return {"connected": bool(self.connected), "mode": self.mode}

    def status(self):
        d = self._driver.status()
        return {
            "connected": self.connected,
            "mode": self.mode,
            "paper": "ok" if d["paper"] == "ok" else "out",
            "cover": d["cover"],
            "overheat": d["overheat"],
        }

    def driver(self):
        return self._driver  # aktif driver instance

cm = ConnectionManager()
