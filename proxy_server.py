import os
import random
import time
import requests
from flask import Flask, request, Response

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

@app.route("/api/proxy")
def proxy():
    target_url = request.args.get("url")
    if not target_url:
        return "Falta ?url=", 400

    ua = random.choice(USER_AGENTS)
    
    # Session Warmup
    session = requests.Session()
    session.headers.update({"User-Agent": ua})
    
    try:
        # Paso 1: Visitar la home para obtener cookies y simular entrada humana
        session.get("https://www.mercadolibre.com.ar/", timeout=10)
        
        # Simular tiempo de lectura/navegación humano
        time.sleep(random.uniform(1.5, 3.5))
        
        # Paso 2: Petición real con headers nivel navegador Chrome en Windows
        headers = {
            "Referer": "https://www.mercadolibre.com.ar/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand)";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        resp = session.get(target_url, headers=headers, timeout=20)
        
        # Detección de bloqueo
        if "suspicious_traffic" in resp.text or "account-verification" in resp.text:
            return "BLOQUEO_DETECTADO", 403

        # Devolver el HTML tal cual
        return Response(
            resp.text,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "text/html; charset=utf-8")
        )
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
