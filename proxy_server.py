import os
import random
import time
from flask import Flask, request, Response
from curl_cffi import requests

app = Flask(__name__)

# Log para verificar que el código arranca
print("@@@ PROXY SERVER BOOTING @@@", flush=True)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    # Log de acceso para debuggear en tiempo real
    print(f"@@@ INCOMING REQUEST @@@ Path: /{path} | Args: {request.args}", flush=True)
    
    target_url = request.args.get("url")
    if not target_url:
        return "Proxy Status: ONLINE. Use ?url=https://...", 200

    session = requests.Session(impersonate="chrome120")
    try:
        headers = {
            "Referer": "https://www.google.com/",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        time.sleep(random.uniform(0.3, 0.8))
        
        print(f"@@@ PROXYING TO: {target_url}", flush=True)
        resp = session.get(target_url, headers=headers, timeout=30)
        print(f"@@@ RESPONSE FROM TARGET: {resp.status_code}", flush=True)
        
        # Detección de bloqueo básico
        html_content = resp.text.lower()
        if "suspicious_traffic" in html_content or "suspicious-traffic" in html_content:
             return "BLOQUEO_DETECTADO", 403

        return Response(
            resp.text,
            status=resp.status_code,
            content_type="text/html; charset=utf-8"
        )
        
    except Exception as e:
        print(f"@@@ ERROR: {str(e)}", flush=True)
        return f"Proxy Error: {str(e)}", 500

if __name__ == "__main__":
    # Koyeb usa el puerto 8080 por defecto para Web Services a veces
    port = int(os.environ.get("PORT", 8080))
    print(f"@@@ RUNNING ON PORT: {port} @@@", flush=True)
    app.run(host="0.0.0.0", port=port)
