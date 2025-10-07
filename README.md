# 🖨️ Printer Service Project (Mock Thermal Printer)

Bu proje, USB ve Ethernet üzerinden haberleşebilen bir termal yazıcı servisi simülasyonudur. Proje, Django ve Django Rest Framework kullanılarak geliştirilmiştir ve temel olarak bir yazdırma servisi API'si ile bu servisin durumunu izlemeyi sağlayan basit bir kullanıcı arayüzü sunar.

![UI Screenshot](https://i.imgur.com/your-screenshot-url.png) <!-- TODO: Buraya bir ekran görüntüsü URL'si ekleyin -->

---

##  архитектура и технологии

- **Backend**: Django, Django Rest Framework
- **Frontend**: Django Templates, HTML, HTMX, TailwindCSS, JavaScript (Fetch API)
- **Veritabanı**: SQLite (varsayılan)
- **Yazıcı Sürücüleri**: Mock (simülasyon) sürücüler. Gerçek bir donanım gerektirmez.
- **Asenkron İşlemler**: Yazdırma işlemleri, `threading` ve `queue` kullanılarak arka planda yönetilir, böylece API istekleri anında yanıt verebilir.

## ✨ Temel Özellikler

- **Çift Modlu Bağlantı**: USB ve LAN (Ethernet) arasında geçiş yapabilme.
- **Otomatik Yeniden Bağlanma**: Bağlantı koptuğunda, artan bekleme süreleri (exponential backoff) ile otomatik olarak yeniden bağlanmayı dener.
- **RESTful API**: Yazdırma, durum sorgulama, logları alma ve yeniden yazdırma işlemleri için temiz ve kullanışlı API endpoint'leri.
- **Hata Yönetimi**: `PAPER_OUT`, `COVER_OPEN` gibi yaygın yazıcı hatalarını simüle eder ve loglar.
- **İş Kuyruğu ve Tekrar Deneme**: Başarısız olan yazdırma işleri, belirli bir deneme sayısına kadar otomatik olarak yeniden denenir.
- **Detaylı Loglama**: Tüm başarılı ve başarısız işlemler, `logs/logs.jsonl` dosyasına JSON formatında kaydedilir.
- **Basit Kullanıcı Arayüzü**:
  - Anlık bağlantı durumunu ve modunu gösterir.
  - Son yazdırma işlerini ve kuyruktaki durumlarını listeler.
  - Hatalı işler için "Tekrar Yazdır" butonu sunar.
- **Farklı İçerik Tipleri**: Metin, görsel (Base64 formatında) ve QR kodu yazdırma desteği.

---

## ⚙️ Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.11+
- Django 5.x  
- Git
- djangorestframework  
- Pillow  
- python-dotenv  

### Adımlar
1.  **Projeyi klonlayın:**
    ```bash
    git clone https://github.com/Mehdic01/printer-service-project.git
    cd printer-service-project/printer-service
    ```

2.  **Python sanal ortamı (virtual environment) oluşturun ve aktif edin:**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```
    ```bash
    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Gerekli paketleri yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **`.env` dosyasını yapılandırın:**
    `.env.example` dosyasını kopyalayarak `.env` adında yeni bir dosya oluşturun. Gerekirse ayarları düzenleyebilirsiniz.
    ```bash
    # Windows
    copy .env.example .env
    ```
    ```bash
    # macOS / Linux
    cp .env.example .env
    ```

5.  **Veritabanı migrasyonlarını uygulayın:**
    ```bash
    python manage.py migrate
    ```

6.  **Geliştirme sunucusunu başlatın:**
    ```bash
    python manage.py runserver 3000
    ```
    Servis artık `http://127.0.0.1:3000` adresinde çalışıyor olacaktır.

---

## 🔌 API Kullanımı

Aşağıda, servisi test etmek için kullanabileceğiniz `curl` istek örnekleri bulunmaktadır.

### 1. Bağlantı Modunu Ayarlama
- **USB moduna geç:**
  ```bash
  curl -X POST http://127.0.0.1:3000/api/connect -H "Content-Type: application/json" -d '{"mode": "usb"}'
  ```
- **LAN moduna geç:**
  ```bash
  curl -X POST http://127.0.0.1:3000/api/connect -H "Content-Type: application/json" -d '{"mode": "lan"}'
  ```

### 2. Yazdırma İşlemleri
- **Metin Yazdırma:**
  ```bash
  curl -X POST http://127.0.0.1:3000/api/print/text -H "Content-Type: application/json" -d '{"text": "Merhaba Dunya!"}'
  ```
- **Görsel Yazdırma (Base64):**
  ```bash
  curl -X POST http://127.0.0.1:3000/api/print/image -H "Content-Type: application/json" -d '{"base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="}'
  ```
- **QR Kodu Yazdırma:**
  ```bash
  curl -X POST http://127.0.0.1:3000/api/print/qr -H "Content-Type: application/json" -d '{"data": "https://github.com/Mehdic01"}'
  ```

### 3. Durum ve Bilgi Alma
- **Yazıcı Durumunu Sorgulama:**
  ```bash
  curl http://127.0.0.1:3000/api/status
  ```
- **Logları Görüntüleme:**
  ```bash
  curl http://127.0.0.1:3000/api/logs
  ```

### 4. Yeniden Yazdırma
- **Başarısız bir işi ID ile tekrar yazdırma:**
  ```bash
  curl -X POST http://127.0.0.1:3000/api/reprint -H "Content-Type: application/json" -d '{"job_id": "abc123xyz"}'
  ```
  *Not: `job_id` değerini UI'dan veya loglardan alabilirsiniz.*

---

## 📝 Loglama Yapısı

Tüm işlemler, `logs/logs.jsonl` dosyasına aşağıdaki şemaya uygun olarak kaydedilir:

```json
{
    "ts": "2025-10-07T10:30:00Z",
    "op": "print_text",
    "conn": "usb",
    "job_id": "f1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "status": "ok"
}
{
    "ts": "2025-10-07T10:35:10Z",
    "op": "print_image",
    "conn": "lan",
    "job_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6e",
    "status": "error",
    "error": {
        "code": "PAPER_OUT",
        "detail": "No paper detected in mock printer."
    },
    "meta": {
        "retries": 1
    }
}
```

## 🧪 Testler

Projenin temel işlevlerini test etmek için Django'nun dahili test mekanizması kullanılabilir:
```bash
python manage.py test printer
```
Bu komut, `printer/tests.py` dosyasındaki testleri çalıştıracaktır.


