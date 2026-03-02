import json

with open("parsed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["appProps"]["pageProps"]["initialState"]["results"]
for i, r in enumerate(results):
    if r.get("id") == "POLYCARD":
        polycard = r.get("polycard", {})
        components = polycard.get("components", [])
        for comp in components:
            if comp.get("type") == "title":
                title_val = comp.get("title")
                print(f"Title value type: {type(title_val)}")
                print(f"Title value: {title_val}")
                if isinstance(title_val, dict):
                    print("Title value keys:", list(title_val.keys()))
        break
