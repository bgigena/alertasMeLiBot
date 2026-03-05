"""
Bot de alertas de MercadoLibre.
Extrae el JSON embebido en la página pública (window.__PRELOADED_STATE__)
— sin API keys, sin OAuth, sin scraping frágil de HTML.

Monitorea nuevas publicaciones de cámaras usadas y envía alertas por Telegram.

Setup:
  1. Copiar .env.example a .env y completar TELEGRAM_TOKEN y TELEGRAM_CHAT_ID
  2. pip install requests python-dotenv beautifulsoup4
  3. python botMeLiAlertas.py

Variables de entorno (.env):
  TELEGRAM_TOKEN    - Token del bot (de @BotFather en Telegram)
  TELEGRAM_CHAT_ID  - ID del chat destino (de @userinfobot en Telegram)
"""

import os
import re
import time
import json
import random
import logging
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
# Cargar .env solo si existe (local). En Koyeb se usan Environment Variables.
if os.path.exists(".env"):
    load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# URL del Proxy (Koyeb o similar)
PROXY_URL = os.getenv("PROXY_URL")
if not PROXY_URL:
    logger.warning("⚠️ PROXY_URL no configurada. El bot podría ser bloqueado fácilmente.")

# URL pública de MercadoLibre con los filtros ya aplicados
ML_URL = (
    "https://listado.mercadolibre.com.ar/camaras-accesorios/camaras/usado/"
    "camara_OrderId_PRICE_PublishedToday_YES_NoIndex_True"
)

SEEN_IDS_FILE = "seen_ids.json"
POLL_INTERVAL_SECONDS = 60
DEBUG_HTML_FILE = "failed_content.html"

# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Pool de User-Agents reales para rotar en cada request y reducir bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

BASE_HEADERS = {
    "Accept-Language": "es-AR,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


# ---------------------------------------------------------------------------
# Scraping de __PRELOADED_STATE__
# ---------------------------------------------------------------------------

def fetch_page_html() -> str | None:
    if PROXY_URL:
        # Normalizar: eliminar el ?url= si ya lo trae para usar params= o concatenación limpia
        base_proxy = PROXY_URL.split('?')[0]
        masked_proxy = base_proxy.split('//')[-1][:25] + "..."
        logger.info(f"Usando proxy: {masked_proxy}")
        
        try:
            # Opción 1: Si no tiene ?, usamos params de requests
            if '?' not in PROXY_URL:
                resp = requests.get(PROXY_URL, params={"url": ML_URL}, timeout=60)
                full_url = resp.url
            else:
                # Opción 2: Si ya tiene ?, concatenamos directamente
                # (Quitando posibles parámetros vacíos como url= finales)
                clean_proxy = PROXY_URL.rstrip('?url=')
                sep = '&' if '?' in clean_proxy else '?'
                full_url = f"{clean_proxy}{sep}url={ML_URL}"
                resp = requests.get(full_url, timeout=60)

            # El proxy devuelve 403 con 'BLOQUEO_DETECTADO' if ML nos frena
            if resp.status_code == 403 and "BLOQUEO_DETECTADO" in resp.text:
                logger.error("🛑 El proxy fue detectado por MercadoLibre (Suspicious Traffic).")
                return None
            
            if resp.status_code != 200:
                logger.error(f"Error con el Proxy: {resp.status_code} url: {full_url}")
                return None

            return resp.text
        except requests.RequestException as e:
            logger.error(f"Error de conexión con el Proxy: {e}")
            return None

    # Request directo (local): rotamos UA y agregamos delay para no ser bloqueados
    delay = random.uniform(3, 10)
    logger.info(f"Esperando {delay:.1f}s antes del request...")
    time.sleep(delay)

    headers = {**BASE_HEADERS, "User-Agent": random.choice(USER_AGENTS)}
    logger.info(f"UA: {headers['User-Agent'][:60]}...")

    try:
        resp = requests.get(ML_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        logger.error(f"Error al cargar la página: {e}")
        return None


def extract_preloaded_state(html: str) -> dict | None:
    """
    Extrae el JSON de la nueva estructura de ML (Nordic Rendering Context).
    Busca window._n.ctx.r = {...} o el tag <script id="__NORDIC_RENDERING_CTX__">
    """
    # Intento 1: tag <script id="__NORDIC_RENDERING_CTX__">
    match = re.search(
        r'<script[^>]+id=["\']__NORDIC_RENDERING_CTX__["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if match:
        content = match.group(1).strip()
        # El contenido puede empezar con _n.ctx.r=
        if content.startswith("_n.ctx.r="):
            content = content[len("_n.ctx.r="):].rstrip(";")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

    # Intento 2: Buscar _n.ctx.r = {...}; en cualquier parte del HTML
    match = re.search(r'_n\.ctx\.r\s*=\s*(\{.*?\});', html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    return None


def _save_debug_html(html: str) -> None:
    try:
        with open(DEBUG_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"HTML de depuración guardado en {DEBUG_HTML_FILE} (tamaño: {len(html)} bytes)")
    except Exception as e:
        logger.error(f"No se pudo guardar el HTML de depuración: {e}")


def parse_items_from_state(state: dict) -> list[dict]:
    """
    Navega la estructura del state para encontrar los items.
    En search-nordic (nueva vers.), están en appProps.pageProps.initialState.results
    """
    try:
        results = state["appProps"]["pageProps"]["initialState"]["results"]
        return _extract_from_results(results)
    except (KeyError, TypeError):
        pass

    # Búsqueda recursiva si la ruta falla
    return _deep_search_results(state)


def _extract_from_results(results: list) -> list[dict]:
    items = []
    for r in results:
        if not isinstance(r, dict):
            continue
        
        # Nueva estructura: POLYCARD
        if r.get("id") == "POLYCARD" and "polycard" in r:
            p = r["polycard"]
            metadata = p.get("metadata", {})
            item_id = metadata.get("id")
            if not item_id:
                continue

            # Extraer título y precio de los components
            title = "Sin título"
            price = None
            currency = "ARS"
            
            for comp in p.get("components", []):
                ctype = comp.get("type")
                if ctype == "title":
                    title = comp.get("title", {}).get("text", title)
                elif ctype == "price":
                    price_data = comp.get("price", {}).get("current_price", {})
                    price = price_data.get("value")
                    currency = price_data.get("currency", currency)

            items.append({
                "id":       str(item_id),
                "title":    title,
                "url":      metadata.get("url", ""),
                "price":    price,
                "currency": currency,
            })
            continue

        # Estructura vieja (legacy/fallback)
        item_id = r.get("id", "")
        if item_id and str(item_id).startswith("MLA"):
            items.append({
                "id":       str(item_id),
                "title":    r.get("title", "Sin título"),
                "url":      r.get("permalink", ""),
                "price":    r.get("price"),
                "currency": r.get("currency_id", "ARS"),
            })
            
    return items


def _deep_search_results(obj, depth=0) -> list[dict]:
    """Búsqueda recursiva de arrays que parezcan listas de items de ML."""
    if depth > 10:
        return []
    if isinstance(obj, list):
        extracted = _extract_from_results(obj)
        if extracted:
            return extracted
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, (dict, list)):
                result = _deep_search_results(v, depth + 1)
                if result:
                    return result
    return []


def fetch_listings() -> list[dict]:
    html = fetch_page_html()
    if not html:
        return []

    state = extract_preloaded_state(html)
    if not state:
        logger.warning("No se encontró __PRELOADED_STATE__ en el HTML. ML puede haber cambiado su estructura.")
        _save_debug_html(html)
        return []

    items = parse_items_from_state(state)
    
    if not items:
        logger.warning("No se encontraron items en el state. ML puede estar bloqueando o enviando una página vacía.")
        _save_debug_html(html)
        
    return items


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def load_seen_ids() -> set:
    if os.path.exists(SEEN_IDS_FILE):
        with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen_ids(ids: set) -> None:
    with open(SEEN_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram_message(text: str) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados.")
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id":                  TELEGRAM_CHAT_ID,
                "text":                     text,
                "parse_mode":               "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("✅ Mensaje enviado a Telegram.")
    except requests.RequestException as e:
        logger.error(f"Error al enviar mensaje a Telegram: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Detalle API Telegram: {e.response.text}")


def build_message(item: dict) -> str:
    price = item.get("price")
    currency = item.get("currency", "ARS")
    price_line = ""
    if price is not None:
        symbol = "$" if currency == "ARS" else currency
        price_str = f"{symbol}{price:,.0f}".replace(",", ".")
        price_line = f"\n💰 <b>{price_str}</b>"
    return (
        "📷 <b>Mati, acaban de publicar una cámara!</b>"
        f"{price_line}\n"
        f"📝 {item['title']}\n"
        f"🔗 <a href='{item['url']}'>Ver publicación en MercadoLibre</a>"
    )


# ---------------------------------------------------------------------------
# Validación inicial
# ---------------------------------------------------------------------------

def validate_config() -> bool:
    missing = []
    if not TELEGRAM_TOKEN:   missing.append("TELEGRAM_TOKEN")
    if not TELEGRAM_CHAT_ID: missing.append("TELEGRAM_CHAT_ID")
    if missing:
        logger.error(f"Faltan variables de entorno: {', '.join(missing)}")
        logger.error("Completá el archivo .env (ver .env.example)")
        return False
    return True


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("=" * 55)
    logger.info("  Bot de alertas MercadoLibre — Cámaras usadas")
    logger.info("=" * 55)

    if not validate_config():
        return

    logger.info(f"URL     : {ML_URL}")
    logger.info(f"Intervalo: {POLL_INTERVAL_SECONDS}s")
    logger.info("")

    seen_ids     = load_seen_ids()
    is_first_run = len(seen_ids) == 0

    if is_first_run:
        logger.info("Primera ejecución: cargando publicaciones existentes sin alertar...")

    while True:
        logger.info("Consultando MercadoLibre...")
        listings = fetch_listings()
        logger.info(f"Publicaciones encontradas: {len(listings)}")

        if is_first_run:
            for item in listings:
                seen_ids.add(item["id"])
            save_seen_ids(seen_ids)
            is_first_run = False
            logger.info(f"Listo. {len(seen_ids)} IDs guardados. Monitoreando nuevas publicaciones...")
        else:
            new_items = [item for item in listings if item["id"] not in seen_ids]
            if new_items:
                logger.info(f"🆕 {len(new_items)} publicación(es) nueva(s)!")
                for item in new_items:
                    logger.info(f"  → [{item['id']}] {item['title']}")
                    send_telegram_message(build_message(item))
                    seen_ids.add(item["id"])
                save_seen_ids(seen_ids)
            else:
                logger.info("Sin publicaciones nuevas.")

        logger.info(f"Próxima consulta en {POLL_INTERVAL_SECONDS}s...\n")
        
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
