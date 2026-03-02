import re
import json

with open("script_18_full.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Try to find _n.ctx.r=({...});
match = re.search(r'_n\.ctx\.r\s*=\s*(\{.*?\});', content, re.DOTALL)
if match:
    json_str = match.group(1)
    print(f"Matched JSON! Len: {len(json_str)}")
    try:
        data = json.loads(json_str)
        print("Success! Parsed JSON.")
        # Check where the results are
        # In current ML search, they are usually in:
        # data["initialState"]["results"] or something similar.
        # Let's explore the data.
        with open("parsed_data.json", "w", encoding="utf-8") as outf:
            json.dump(data, outf, indent=2)
            
        print("Keys in root:", list(data.keys()))
        if "appProps" in data:
            print("appProps keys:", list(data["appProps"].keys()))
            if "pageProps" in data["appProps"]:
                print("pageProps keys:", list(data["appProps"]["pageProps"].keys()))
                # Often it's in initialData or results
                if "results" in data["appProps"]["pageProps"]:
                    results = data["appProps"]["pageProps"]["results"]
                    print(f"Found {len(results)} results in appProps.pageProps.results")
                    for i, r in enumerate(results[:3]):
                        print(f"Result {i}: {r.get('id')} - {r.get('title')}")
                elif "initialData" in data["appProps"]["pageProps"]:
                    idat = data["appProps"]["pageProps"]["initialData"]
                    print("initialData keys:", list(idat.keys()))
                    if "results" in idat:
                        results = idat["results"]
                        print(f"Found {len(results)} results in initialData.results")
    except Exception as e:
        print(f"Failed to parse: {e}")
else:
    print("Could not find _n.ctx.r=({...}); in the script.")
