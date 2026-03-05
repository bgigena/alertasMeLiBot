import os
import random
import time
import sys
from flask import Flask, request, Response
from curl_cffi import requests

app = Flask(__name__)

# Catch-all para que nada devuelva 404
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def handle_all(path):
    target_url = request.args.get("url")
    
    # Log para ver qué llega exactamente
    print(f"DEBUG INCOMING: Path='{path}', Args='{request.args}'", flush=True)
    
    if not target_url:
        return f"Proxy is running! Path: {path}. Use ?url=https://...", 200

    session = requests.Session(impersonate="chrome120")
    
    try:
        headers = {
            "Referer": "https://www.google.com/",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        time.sleep(random.uniform(0.3, 0.8))
        
        print(f"DEBUG PROXYING TO: {target_url}", flush=True)
        resp = session.get(target_url, headers=headers, timeout=30)
        print(f"DEBUG PROXY RESP: Status {resp.status_code}", flush=True)
        
        html_content = resp.text.lower()
        block_triggers = ["suspicious_traffic", "suspicious-traffic", "account-verification", "robot", "captcha"]
        
        if any(trigger in html_content for trigger in block_triggers) or resp.status_code == 403:
            print("DEBUG: BLOQUEO DETECTADO EN EL HTML", flush=True)
            return "BLOQUEO_DETECTADO", 403

        return Response(
            resp.text,
            status=resp.status_code,
            content_type="text/html; charset=utf-8"
        )
        
    except Exception as e:
        print(f"DEBUG PROXY ERROR: {str(e)}", flush=True)
        return f"Error en Proxy: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # Forzar logs a stdout
    app.run(host="0.0.0.0", port=port, debug=False)
