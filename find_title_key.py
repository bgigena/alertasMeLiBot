import json

with open("parsed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["appProps"]["pageProps"]["initialState"]["results"]
for i, r in enumerate(results):
    if r.get("id") == "POLYCARD":
        polycard = r.get("polycard", {})
        components = polycard.get("components", [])
        print(f"--- Result {i} (POLYCARD) components ---")
        for comp in components:
            if comp.get("type") == "title":
                print("Title component keys:", list(comp.keys()))
                # Find any string that looks like a title
                for k, v in comp.items():
                    if isinstance(v, str):
                        print(f"  {k}: {v}")
        break
