import re
import json
import requests

ML_URL = (
    "https://listado.mercadolibre.com.ar/camaras-accesorios/camaras/usado/"
    "camara_OrderId_PRICE_PublishedToday_YES_NoIndex_True"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

print("Descargando página...")
resp = requests.get(ML_URL, headers=HEADERS, timeout=20)
print(f"Status: {resp.status_code}")
html = resp.text
print(f"HTML length: {len(html)} chars")

# 1. Buscar scripts con id __PRELOADED_STATE__
matches = re.findall(r'<script[^>]+id=["\']([^"\']*)["\'][^>]*>', html)
print(f"\nScript IDs encontrados: {matches}")

# 2. Ver si existe __PRELOADED_STATE__ en el texto
if "__PRELOADED_STATE__" in html:
    print("✅ __PRELOADED_STATE__ ENCONTRADO en el HTML")
    idx = html.index("__PRELOADED_STATE__")
    print(f"Contexto (chars 0-300 del match):\n{html[idx:idx+300]}")
else:
    print("❌ __PRELOADED_STATE__ NO encontrado")

# 3. Buscar MLA IDs en el HTML como indicador de que hay datos
mla_ids = re.findall(r'"id"\s*:\s*"(MLA\d+)"', html)
print(f"\nMLA IDs encontrados en el HTML: {len(mla_ids)}")
if mla_ids:
    print(f"Primeros 5: {mla_ids[:5]}")

# 4. Buscar scripts que contengan permalink
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"\nTotal de script tags: {len(scripts)}")
for i, s in enumerate(scripts):
    if "permalink" in s or "MLA" in s:
        print(f"\n--- Script {i} (len={len(s)}) ---")
        print(s[:600])
        print("...")
        break

# 5. Guardar el HTML completo para inspección manual
with open("ml_debug_page.html", "w", encoding="utf-8") as f:
    f.write(html)
print("\nHTML guardado en ml_debug_page.html")
