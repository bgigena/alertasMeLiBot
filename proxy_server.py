import os
import random
import time
from flask import Flask, request, Response
from curl_cffi import requests

app = Flask(__name__)

# Intentamos imitar un navegador Chrome moderno lo más fielmente posible.
# curl_cffi con impersonate ya maneja el TLS fingerprint (JA3).

@app.route("/api/proxy")
def proxy():
    target_url = request.args.get("url")
    if not target_url:
        return "Falta ?url=", 400

    # Usamos curl_cffi para imitar el TLS de Chrome (imprescindible para ML avanzado)
    session = requests.Session(impersonate="chrome120")
    
    try:
        # Eliminamos el "Warmup" que podría estar ensuciando la sesión si la IP ya es sospechosa.
        # Vamos directo al grano con un header de Referer falso.
        headers = {
            "Referer": "https://www.google.com/",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # Simular un delay de red antes de la petición real
        time.sleep(random.uniform(0.5, 2.0))
        
        resp = session.get(target_url, headers=headers, timeout=30)
        
        # Detección de bloqueo mejorada
        html_content = resp.text.lower()
        block_triggers = [
            "suspicious_traffic", 
            "suspicious-traffic", 
            "account-verification",
            "robot",
            "captcha"
        ]
        
        if any(trigger in html_content for trigger in block_triggers) or resp.status_code == 403:
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
