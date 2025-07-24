from flask import Flask, request, render_template
from datetime import datetime, timedelta
import threading, time, requests
import pytz

app = Flask(__name__, template_folder='templates')
SON_UYANIS = None
trtz = pytz.timezone("Europe/Istanbul")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/uyandi", methods=["POST"])
def uyandi():
    global SON_UYANIS
    data = request.get_json()
    SON_UYANIS = datetime.fromisoformat(data["saat"]).astimezone(trtz)
    print(f"Uyanış saati kaydedildi: {SON_UYANIS}")
    return {"ok": True}

def kontrol_et():
    global SON_UYANIS
    while True:
        if SON_UYANIS:
            simdi = datetime.now(trtz)
            fark = simdi - SON_UYANIS
            print(f"Kontrol ediliyor... Son uyanış: {SON_UYANIS}, Fark: {fark}")
            if fark > timedelta(hours=3):
                print("3 saat geçti, bildirim gönderiliyor...")
                try:
                    requests.post("https://ntfy.sh/ecrin", data="💕 3 saattir uyanıksın Ecrin... biraz dinlensen mi aşkım?".encode('utf-8'))
                    print("Bildirim gönderildi.")
                except Exception as e:
                    print(f"Bildirim gönderilemedi: {e}")
                SON_UYANIS = None
        time.sleep(60)

# Arka plan görevini başlat
threading.Thread(target=kontrol_et, daemon=True).start()
