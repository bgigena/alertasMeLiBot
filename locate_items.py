import json

with open("parsed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

initialState = data["appProps"]["pageProps"]["initialState"]
print("initialState keys:", list(initialState.keys()))

if "results" in initialState:
    results = initialState["results"]
    print(f"Found {len(results)} results in initialState.results")
    for i, r in enumerate(results[:3]):
        print(f"Result {i}: {r.get('id')} - {r.get('title')}")
elif "listingState" in initialState and "results" in initialState["listingState"]:
    results = initialState["listingState"]["results"]
    print(f"Found {len(results)} results in initialState.listingState.results")
elif "searchReducer" in initialState and "results" in initialState["searchReducer"]:
    results = initialState["searchReducer"]["results"]
    print(f"Found {len(results)} results in initialState.searchReducer.results")
