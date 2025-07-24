from flask import Flask, request, render_template
from datetime import datetime, timedelta
import threading, time, requests
import pytz

app = Flask(__name__, template_folder='templates')

# Sunucu her yeniden başladığında sıfırlanacak global değişkenler
son_uyanis_verisi = {
    "zaman": None,
    "dev_mode": False
}

trtz = pytz.timezone("Europe/Istanbul")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/uyandi", methods=["POST"])
def uyandi():
    global son_uyanis_verisi
    data = request.get_json()

    son_uyanis_verisi["zaman"] = datetime.fromisoformat(data["saat"]).astimezone(trtz)
    son_uyanis_verisi["dev_mode"] = data.get("devMode", False)

    mod = "Geliştirici" if son_uyanis_verisi["dev_mode"] else "Normal"
    print(f"Uyanış saati kaydedildi ({mod} Mod): {son_uyanis_verisi['zaman']}")

    return {"ok": True}

def kontrol_et():
    global son_uyanis_verisi
    while True:
        time.sleep(60) # Her dakika kontrol et

        if not son_uyanis_verisi["zaman"]:
            continue

        simdi = datetime.now(trtz)
        fark = simdi - son_uyanis_verisi["zaman"]

        bekleme_suresi = timedelta(minutes=2) if son_uyanis_verisi["dev_mode"] else timedelta(hours=3)
        mod = "Geliştirici (2dk)" if son_uyanis_verisi["dev_mode"] else "Normal (3sa)"

        print(f"Kontrol ediliyor ({mod})... Son uyanış: {son_uyanis_verisi['zaman']}, Fark: {fark.total_seconds():.0f}s")

        if fark > bekleme_suresi:
            print(f"{mod} süresi doldu, bildirim gönderiliyor...")
            try:
                mesaj = f"💕 {int(bekleme_suresi.total_seconds() / 60)} dakikadır uyanıksın Ecrin... biraz dinlensen mi aşkım?"
                requests.post("https://ntfy.sh/ecrin", data=mesaj.encode('utf-8'))
                print("Bildirim gönderildi.")
            except Exception as e:
                print(f"Bildirim gönderilemedi: {e}")
            finally:
                # Bildirim gönderildikten sonra zamanı sıfırla
                son_uyanis_verisi["zaman"] = None
                son_uyanis_verisi["dev_mode"] = False


# Arka plan görevini başlat
threading.Thread(target=kontrol_et, daemon=True).start()
