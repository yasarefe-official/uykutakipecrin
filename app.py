from flask import Flask, render_template, request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# ntfy.sh topic'inizi buraya girin. Gizli tutmak için ortam değişkeni kullanmak en iyisidir.
NTFY_TOPIC = os.environ.get('NTFY_TOPIC', 'ecrinin-uyku-zamani-test')

# Arka plan görevleri için zamanlayıcı
scheduler = BackgroundScheduler(daemon=True)

def send_notification():
    """ntfy.sh'e bildirim gönderir."""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data="Ecrin, uyku zamanı geldi! 😴 Hadi yatağa! 💖".encode('utf-8'),
            headers={
                "Title": "Uyku Zamanı Hatırlatıcısı",
                "Priority": "high",
                "Tags": "bed,moon"
            }
        )
        logging.info(f"'{NTFY_TOPIC}' konusuna bildirim gönderildi.")
    except Exception as e:
        logging.error(f"Bildirim gönderilemedi: {e}")

@app.route('/')
def index():
    """Ana sayfayı, yani index.html'i sunar."""
    return render_template('index.html')

@app.route('/notify', methods=['POST'])
def notify():
    """Bildirim zamanlamak için endpoint."""
    data = request.get_json()
    is_dev_mode = data.get('devMode', False)

    # Geliştirici modunda 2 dakika, normal modda 3 saat (180 dakika) sonra
    delay_minutes = 2 if is_dev_mode else 180

    # Mevcut zamanlanmış görevleri temizle (varsa)
    for job in scheduler.get_jobs():
        if job.name == 'send_notification':
            job.remove()
            logging.info("Mevcut bildirim görevi iptal edildi.")

    # Yeni bildirim görevini zamanla
    scheduler.add_job(
        send_notification,
        'interval',
        minutes=delay_minutes,
        id='timed_notification',
        name='send_notification',
        replace_existing=True
    )

    logging.info(f"Bildirim {delay_minutes} dakika sonrasına zamanlandı.")
    return {"status": "success", "message": f"Notification scheduled in {delay_minutes} minutes."}, 200

def keep_alive():
    """Uygulamayı uyanık tutmak için periyodik görev."""
    logging.info("Keep-alive sinyali. Uygulama çalışıyor.")

# Uygulama başladığında zamanlayıcıyı başlat
scheduler.add_job(keep_alive, 'interval', minutes=5, id='keep_alive_job')
scheduler.start()

if __name__ == '__main__':
    # Render'ın beklediği gibi 0.0.0.0'da ve dinamik portta çalıştır.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
