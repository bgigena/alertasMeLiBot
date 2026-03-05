import os
import random
import time
from flask import Flask, request, Response
from curl_cffi import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Proxy is running! Use /api/proxy?url=..."

@app.route("/api/proxy")
def proxy():
    target_url = request.args.get("url")
    if not target_url:
        return "Falta ?url=", 400

    session = requests.Session(impersonate="chrome120")
    
    try:
        headers = {
            "Referer": "https://www.google.com/",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # Delay para no ser instantáneo
        time.sleep(random.uniform(0.5, 1.5))
        
        resp = session.get(target_url, headers=headers, timeout=30)
        
        # Detección de bloqueo
        html_content = resp.text.lower()
        block_triggers = ["suspicious_traffic", "suspicious-traffic", "account-verification", "robot", "captcha"]
        
        if any(trigger in html_content for trigger in block_triggers) or resp.status_code == 403:
            return "BLOQUEO_DETECTADO", 403

        return Response(
            resp.text,
            status=resp.status_code,
            content_type="text/html; charset=utf-8"
        )
        
    except Exception as e:
        return f"Error en Proxy: {str(e)}", 500

if __name__ == "__main__":
    # Importante: Escuchar en 0.0.0.0 y usar el puerto de Koyeb
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
