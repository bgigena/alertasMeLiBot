import os
import random
import time
from flask import Flask, request, Response
from curl_cffi import requests

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

@app.route("/api/proxy")
def proxy():
    target_url = request.args.get("url")
    if not target_url:
        return "Falta ?url=", 400

    ua = random.choice(USER_AGENTS)
    
    # Usamos curl_cffi para imitar el TLS de Chrome (imprescindible para ML avanzado)
    session = requests.Session(impersonate="chrome120")
    
    try:
        # Paso 1: Warmup (opcional con curl_cffi pero ayuda por las cookies)
        session.get("https://www.mercadolibre.com.ar/", timeout=15)
        
        # Simular lectura humana
        time.sleep(random.uniform(1.0, 2.5))
        
        # Paso 2: Petición real con impersonate de Chrome
        # curl_cffi ya maneja los headers y el TLS stack automáticamente al usar 'impersonate'
        resp = session.get(target_url, timeout=30)
        
        # Detección de bloqueo mejorada (buscamos varias formas de bloqueo)
        html_content = resp.text.lower()
        block_triggers = [
            "suspicious_traffic", 
            "suspicious-traffic", 
            "account-verification",
            "para continuar, ingresa a tu cuenta"
        ]
        
        if any(trigger in html_content for trigger in block_triggers):
            return "BLOQUEO_DETECTADO", 403

        # Devolver el HTML
        return Response(
            resp.text,
            status=resp.status_code,
            content_type="text/html; charset=utf-8"
        )
        
    except Exception as e:
        return f"Error en Proxy: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
