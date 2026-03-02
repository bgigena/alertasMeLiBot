import json

with open("parsed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["appProps"]["pageProps"]["initialState"]["results"]
for i, r in enumerate(results):
    if r.get("id") == "POLYCARD":
        polycard = r.get("polycard", {})
        print(f"--- Result {i} (POLYCARD) ---")
        print("polycard keys:", list(polycard.keys()))
        # Check 'content' inside polycard if exists
        # Or maybe directly 'title', 'price' etc.
        for k, v in polycard.items():
            if isinstance(v, (str, int, float)):
                print(f"  {k}: {v}")
            elif isinstance(v, dict):
                # Check for item_id or similar in nested dicts
                if "id" in v: print(f"  {k}.id: {v['id']}")
                if "item_id" in v: print(f"  {k}.item_id: {v['item_id']}")
        break
