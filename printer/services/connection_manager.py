class ConnectionManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.mode = "mock"
            cls._instance.connected = False
            cls._instance.last_error = None
        return cls._instance

    def connect(self, mode="mock", **kwargs):
        self.mode = mode
        # burada gerçek USB/LAN yerine mock bağlanıyoruz
        self.connected = True
        self.last_error = None
        return {"connected": True, "mode": self.mode}

    def status(self):
        # ileride PAPER_OUT vb. simülasyonları buradan vereceğiz
        return {
            "connected": self.connected,
            "mode": self.mode,
            "paper": "ok",
            "cover": "closed",
            "overheat": False,
        }


cm = ConnectionManager()
