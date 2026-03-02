import json

with open("parsed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["appProps"]["pageProps"]["initialState"]["results"]
for i, r in enumerate(results):
    if r.get("id") == "POLYCARD":
        print(f"--- Result {i} (POLYCARD) ---")
        # Print keys of the polycard object
        print("Keys:", list(r.keys()))
        # Usually data is in 'content' or 'data'
        if "content" in r:
            content = r["content"]
            print("content keys:", list(content.keys()))
            # Print first few fields of content
            for k, v in content.items():
                if isinstance(v, (str, int, float)):
                    print(f"  {k}: {v}")
                elif k == "id":
                    print(f"  item_id: {v}")
        break
