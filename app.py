from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Ana sayfayı, yani index.html'i sunar."""
    return render_template('index.html')

if __name__ == '__main__':
    # Render'ın beklediği gibi 0.0.0.0'da ve dinamik portta çalıştır.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
