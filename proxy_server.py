import os
import random
import time
from flask import Flask, request, Response
from curl_cffi import requests

app = Flask(__name__)

# Log simple para ver si el server arranca
print("@@@ PROXY SERVER STARTING @@@", flush=True)

@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def main_proxy():
    target_url = request.args.get("url")
    
    print(f"@@@ REQUEST RECEIVED @@@ URL: {target_url}", flush=True)
    
    if not target_url:
        return "Proxy is ALIVE. Use ?url=...", 200

    session = requests.Session(impersonate="chrome120")
    
    try:
        headers = {
            "Referer": "https://www.google.com/",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # Un delay mínimo
        time.sleep(0.5)
        
        print(f"@@@ FETCHING: {target_url}", flush=True)
        resp = session.get(target_url, headers=headers, timeout=30)
        print(f"@@@ DONE: Status {resp.status_code}", flush=True)
        
        # Si ML devuelve 404, pasamos ese 404 al bot
        if resp.status_code == 404:
             return "MERCADOLIBRE_RETURNED_404", 404
             
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
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
