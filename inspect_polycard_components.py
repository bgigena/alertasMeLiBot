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
            ctype = comp.get("type")
            print(f"Component: {ctype}")
            # Usually 'title' type has the title
            # 'price' type has the price
            # There might be a 'link' or similar
            if ctype == "title":
                print("  Title:", comp.get("text"))
            elif ctype == "price":
                # Price is often nested
                print("  Price data:", comp.get("price"))
            elif ctype == "link":
                print("  Link:", comp.get("href"))
        
        # Also check for permalink in the root of polycard or metadata
        metadata = polycard.get("metadata", {})
        print("Metadata keys:", list(metadata.keys()))
        if "permalink" in metadata:
            print("  Permalink in metadata:", metadata["permalink"])
        break
