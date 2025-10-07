from django.db import models

class PrintJob(models.Model):
    TYPE_CHOICES = [("text","text"),("image","image"),("qr","qr")] #farkli icerik tipleri: text, image, qr
    STATUS_CHOICES = [("pending","pending"),("running","running"),("ok","ok"),("error","error")]

    job_id = models.CharField(max_length=32, unique=True, db_index=True) 
    idem_key = models.CharField(max_length=64, null=True, blank=True, db_index=True) #ayni icerik icin tekrar gonderilen isteklerde kullanilacak
    type = models.CharField(max_length=10, choices=TYPE_CHOICES) #text, image, qr
    payload = models.JSONField() #text, image, qr icin gerekli veriler
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending") #pending, running, ok, error
    error_code = models.CharField(max_length=32, null=True, blank=True)  
    retries = models.IntegerField(default=0) #kac kere denendi
    conn_mode_snapshot = models.CharField(max_length=8, default="mock") #o anki baglanti modu
    created_at = models.DateTimeField(auto_now_add=True) #olusturulma tarihi
    updated_at = models.DateTimeField(auto_now=True) #guncellenme tarihi

    def __str__(self):
        return f"{self.job_id} {self.type} {self.status}"
