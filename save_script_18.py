import re

with open("ml_debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
script_18 = scripts[18]

with open("script_18_full.txt", "w", encoding="utf-8") as outf:
    outf.write(script_18)

print(f"Saved script 18 (len={len(script_18)}) to script_18_full.txt")
print("End of script:", script_18[-200:])
