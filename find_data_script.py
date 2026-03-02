import re

with open("ml_debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# MLA IDs were found in the HTML. Let's see which script they are in.
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

for i, s in enumerate(scripts):
    if "MLA" in s and "item_id" in s:
        print(f"Script {i} (len={len(s)}) contains MLA and item_id")
        print("Start:", s[:200])
        # Find more context around an item_id
        match = re.search(r'\{"item_id":"MLA\d+",.*?\}', s)
        if match:
            print("Example item:", match.group(0))
        
        # Save first part of this script
        with open(f"script_data_{i}.txt", "w", encoding="utf-8") as outf:
            outf.write(s[:50000]) # Large snippet

