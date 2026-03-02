import re
import json

with open("ml_debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Try to find all script contents
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

# Target script 18 (based on previous run)
script = scripts[18]

# Find the start and end of the JSON object
# It usually starts with { and ends before melidata or );
# Let's find the first { and the last } that is not followed by much
match = re.search(r'(\{.*\})', script, re.DOTALL)
if match:
    content = match.group(1)
    
    # If it ends with ); we need to strip it
    # But wait, greediness might include );melidata(...) in the match if it ends with )
    # Let's try to find the last valid JSON character
    
    # Alternative: use a more specific regex for the state
    # Often it looks like window.__NORDIC_CORE_CTX__ = {...};
    # or just ({...});
    
    # Try common assignments
    re_patterns = [
        r'window\.__NORDIC_CORE_CTX__\s*=\s*(\{.*?\});',
        r'window\.__NORDIC_RENDERING_CTX__\s*=\s*(\{.*?\});',
        r'\(((\{.*?\}));\s*melidata',
        r'(\{.*?\})\s*\);\s*melidat',
    ]
    
    found = False
    for pat in re_patterns:
        m = re.search(pat, script, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                print(f"Parsed JSON using pattern {pat}!")
                with open("data_extracted.json", "w", encoding="utf-8") as outf:
                    json.dump(data, outf, indent=2)
                found = True
                break
            except:
                pass
    
    if not found:
        # Final fallback: take everything between first { and last }
        # and try to fix it
        start = script.find('{')
        end = script.rfind('}')
        if start != -1 and end != -1:
            content = script[start:end+1]
            try:
                data = json.loads(content)
                print("Parsed JSON using first/last { }!")
                with open("data_extracted.json", "w", encoding="utf-8") as outf:
                    json.dump(data, outf, indent=2)
                found = True
            except Exception as e:
                print(f"Fallback failed: {e}")
                # Save first 1000 and last 1000 characters for debugging
                with open("failed_content.txt", "w", encoding="utf-8") as df:
                    df.write(content[:1000] + "\n...\n" + content[-1000:])
                    
