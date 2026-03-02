import re
import json
import os

html_path = "ml_debug_page.html"
if not os.path.exists(html_path):
    print(f"Error: {html_path} not found")
    exit(1)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Try to find all script contents
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

print(f"Total scripts found: {len(scripts)}")

for i, script in enumerate(scripts):
    # Check if this script looks like it has item data
    if "MLA" in script and "permalink" in script:
        print(f"\n--- Script {i} has MLA and permalink (len={len(script)}) ---")
        
        # Try to find the largest JSON block
        # Usually it's an assignment or a function call argument
        # We'll look for something starting with { and ending with }
        json_matches = re.finditer(r'(\{.*\})', script, re.DOTALL)
        for j, mj in enumerate(json_matches):
            content = mj.group(1)
            # Try to parse it as JSON (might need cleaning)
            try:
                # Basic cleaning: remove trailing ); or similar if it's a function call
                clean_content = content
                if clean_content.endswith(");"): clean_content = clean_content[:-2]
                
                data = json.loads(clean_content)
                print(f"  Match {j}: Successfully parsed JSON! Keys: {list(data.keys())[:10]}")
                
                # Check for results
                # In newer versions it might be in components -> results
                # or similar. Let's dump the keys deeper.
                if "results" in clean_content:
                    print("  'results' found in this JSON")
                    # Save a bit of it
                    with open(f"data_script_{i}.json", "w", encoding="utf-8") as outf:
                        json.dump(data, outf, indent=2)
                    print(f"  Saved to data_script_{i}.json")
            except Exception as e:
                # If it fails, maybe it's not a pure JSON
                print(f"  Match {j}: Failed to parse JSON: {str(e)[:100]}")
                # Save first 500 chars for inspection
                print(f"  Snippet: {content[:200]}...")

