import re

with open("ml_debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Look for <script id="__NORDIC_CORE_CTX__">...</script>
pattern = r'<script[^>]+id=["\']__NORDIC_CORE_CTX__["\'][^>]*>(.*?)</script>'
match = re.search(pattern, html, re.DOTALL)

if match:
    content = match.group(1)
    print(f"Found __NORDIC_CORE_CTX__ script! Len: {len(content)}")
    print("Start:", content[:200])
    print("End:", content[-200:])
else:
    print("Script with id __NORDIC_CORE_CTX__ not found by regex.")
    # Try finding it by searching for the id and then finding the bounds
    idx = html.find('id="__NORDIC_CORE_CTX__"')
    if idx != -1:
        print(f"Found ID at index {idx}")
        # Look for the closing > and then the next </script>
        start_data = html.find('>', idx) + 1
        end_data = html.find('</script>', start_data)
        if start_data != 0 and end_data != -1:
            content = html[start_data:end_data]
            print(f"Extracted content! Len: {len(content)}")
            print("Start:", content[:200])
            print("End:", content[-200:])
            
            # Save it
            with open("ctx_content.txt", "w", encoding="utf-8") as outf:
                outf.write(content)
