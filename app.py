from flask import Flask, request, render_template, jsonify
from datetime import datetime
import pytz

app = Flask(__name__, template_folder='templates')

# Saat dilimini ayarla
trtz = pytz.timezone("Europe/Istanbul")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/uyandi", methods=["POST"])
def uyandi():
    try:
        data = request.get_json()
        # Gelen ISO formatındaki saati alıp Türkiye saat dilimine çeviriyoruz
        uyanis_saati_str = data["saat"]
        uyanis_saati = datetime.fromisoformat(uyanis_saati_str.replace('Z', '+00:00')).astimezone(trtz)

        # Burada normalde bu veriyi bir veritabanına kaydedersiniz.
        # Bu örnekte sadece konsola yazdırıyoruz.
        print(f"Uyanış saati başarıyla kaydedildi: {uyanis_saati.strftime('%Y-%m-%d %H:%M:%S')}")

        return jsonify({"ok": True}), 200
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return jsonify({"ok": False, "error": "Geçersiz veri"}), 400
