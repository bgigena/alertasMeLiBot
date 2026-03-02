import re

with open("ml_debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

for i, s in enumerate(scripts):
    if "__NORDIC_CORE_CTX__" in s:
        print(f"Script {i} (len={len(s)}):")
        print(s[:300])
        print("...")
        print(s[-300:])
        print("-" * 40)
