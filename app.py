from flask import Flask, render_template, request, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from pywebpush import webpush, WebPushException
from py_vapid import Vapid
import logging
import os
import json
from datetime import datetime, timedelta

# -- Temel Kurulum --
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__, static_folder='static', template_folder='templates')
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# -- VAPID Anahtar Yönetimi --
# Canlı ortamda bu anahtarları ortam değişkenlerinden okumak ZORUNLUDUR.
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_CLAIMS = {"sub": "mailto:your-email@example.com"} # Burayı kendi e-postanızla değiştirin

if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
    logging.warning("VAPID anahtarları ortam değişkenlerinde bulunamadı. Yeni anahtarlar oluşturuluyor.")
    logging.warning("LÜTFEN BU ANAHTARLARI KOPYALAYIP RENDER ORTAM DEĞİŞKENLERİNE EKLEYİN.")
    vapid = Vapid()
    vapid_keys = vapid.generate_keys()
    VAPID_PRIVATE_KEY = vapid_keys["private_key"]
    VAPID_PUBLIC_KEY = vapid_keys["public_key"]
    logging.warning(f"VAPID_PRIVATE_KEY={VAPID_PRIVATE_KEY}")
    logging.warning(f"VAPID_PUBLIC_KEY={VAPID_PUBLIC_KEY}")

# -- Veri Saklama (Basit Yaklaşım) --
# Canlı bir uygulamada burası bir veritabanı olmalıdır.
# Bu örnekte, sunucu yeniden başladığında kaybolacak olan bir global değişkende tutuyoruz.
push_subscription = None

# -- Push Bildirim Fonksiyonu --
def send_push_notification(subscription_info, message_body):
    logging.info("Push bildirimi gönderiliyor...")
    try:
        webpush(
            subscription_info=subscription_info,
            data=message_body,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS.copy()
        )
        logging.info("Push bildirimi başarıyla gönderildi.")
    except WebPushException as ex:
        logging.error(f"Push bildirimi gönderilemedi: {ex}")
        # Hatalı veya süresi dolmuş abonelikleri burada temizleyebilirsiniz.
        if ex.response and ex.response.status_code == 410:
            logging.warning("Abonelik süresi dolmuş veya geçersiz. Temizleniyor.")
            global push_subscription
            push_subscription = None

# -- Route'lar (Endpoints) --
@app.after_request
def add_security_headers(response):
    """Tarayıcı kısıtlamalarını önlemek için gerekli güvenlik başlıklarını ekle."""
    response.headers['Permissions-Policy'] = 'notifications=*'
    return response

@app.route('/')
def index():
    return render_template('index.html', vapid_public_key=VAPID_PUBLIC_KEY)

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(os.getcwd(), 'service-worker.js')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    global push_subscription
    subscription_info = request.get_json()
    if not subscription_info:
        return jsonify({'error': 'Abonelik bilgisi eksik.'}), 400

    logging.info("Yeni bir push aboneliği alındı.")
    push_subscription = subscription_info
    return jsonify({'status': 'success'}), 201

@app.route('/set-alarm', methods=['POST'])
def set_alarm():
    if not push_subscription:
        return jsonify({'error': 'Kullanıcı push aboneliği bulunamadı.'}), 400

    data = request.get_json()
    is_dev_mode = data.get('devMode', False)
    delay_minutes = 2 if is_dev_mode else 180

    # Mevcut alarm görevini iptal et
    if scheduler.get_job('sleep_alarm'):
        scheduler.remove_job('sleep_alarm')
        logging.info("Mevcut alarm iptal edildi.")

    # Yeni alarm görevini zamanla
    run_date = datetime.now() + timedelta(minutes=delay_minutes)
    scheduler.add_job(
        id='sleep_alarm',
        func=send_push_notification,
        trigger='date',
        run_date=run_date,
        args=[push_subscription, "Ecrin, uyku zamanı geldi! 😴 Hadi yatağa! 💖"]
    )

    logging.info(f"Alarm, çalışmak üzere {run_date.strftime('%Y-%m-%d %H:%M:%S')} tarihine zamanlandı.")
    return jsonify({'status': 'success', 'message': f"Alarm {delay_minutes} dakika sonrasına kuruldu."}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
