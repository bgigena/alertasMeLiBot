import os
from flask import Flask

app = Flask(__name__)

# Simplemente un log para ver que arranca
print("@@@ HELLO WORLD APP BOOTING @@@", flush=True)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def hello_world(path):
    print(f"@@@ INCOMING REQUEST @@@ Path: /{path}", flush=True)
    return f"¡HOLA KOYEB! El puerto está abierto. Ruta: /{path}", 200

if __name__ == "__main__":
    # Sincronizamos con el 8080 que configuraste
    port = int(os.environ.get("PORT", 8080))
    print(f"@@@ RUNNING ON PORT: {port} @@@", flush=True)
    app.run(host="0.0.0.0", port=port)
