import urllib.request
import json

def test_endpoint(name, url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            items = data.get("items", data.get("results", []))
            print(f"{name}: Status 200, items count = {len(items)}")
            if items:
                item = items[0]
                print(f"   First item title: {item.get('title')}")
                print(f"   Provenance: {item.get('provenance')}")
                print(f"   Relevance tier: {item.get('inspiration_relevance_tier')}")
                print(f"   Media status: {item.get('media_status')}")
    except Exception as e:
        print(f"{name}: Error {e}")

if __name__ == "__main__":
    test_endpoint("Feed Kota Stone", "http://localhost:8000/api/feed?q=Kota+stone")
    test_endpoint("Feed AAC Block", "http://localhost:8000/api/feed?q=AAC+block")
    test_endpoint("Catalogue AAC", "http://localhost:8000/api/catalogue/materials?q=AAC")

