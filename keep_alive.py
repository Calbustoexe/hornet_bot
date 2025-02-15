from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de Flask : {type(e).__name__} - {e}")

def keep_alive():
    try:
        t = Thread(target=run)
        t.start()
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du thread : {type(e).__name__} - {e}")