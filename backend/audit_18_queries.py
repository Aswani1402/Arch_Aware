import urllib.request
import urllib.parse
import json

QUERIES_TO_AUDIT = [
    "Different types of bricks for a house",
    "Exposed brick wall",
    "AAC block wall",
    "Laterite wall",
    "Rammed earth wall",
    "Marble flooring",
    "Wood-look tiles",
    "Screws and bolts",
    "Electrical switches and switchboards",
    "Exterior lighting",
    "Rainwater drainage",
    "Garden waterfall",
    "House renovation before and after",
    "Kerala traditional house",
    "Modern tropical architecture",
    "Small bathroom design",
    "Kitchen storage",
    "Construction site walkthrough"
]

def audit():
    print("=" * 100)
    print("ARCHITECT AI — AUDITING 18 EXACT SEARCH QUERIES VIA LIVE API")
    print("=" * 100)
    
    results_summary = []

    for q in QUERIES_TO_AUDIT:
        encoded_q = urllib.parse.quote(q)
        url = f"http://127.0.0.1:8000/api/feed?q={encoded_q}&page_size=20"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                total = data.get("total", 0)
                
                print(f"\nQUERY: '{q}' -> Count: {len(items)} (Total in DB: {total})")
                
                titles = []
                duplicates = []
                seen_titles = set()
                
                for idx, item in enumerate(items, 1):
                    t = item.get("title")
                    plat = item.get("source_platform")
                    tags = item.get("material_tags")
                    media = item.get("media_url") or item.get("thumbnail_url")
                    source = item.get("source_url")
                    
                    if t in seen_titles:
                        duplicates.append(t)
                    seen_titles.add(t)
                    
                    titles.append({
                        "rank": idx,
                        "title": t,
                        "platform": plat,
                        "tags": tags,
                        "media_url": media,
                        "source_url": source
                    })
                    print(f"  [{idx}] [{plat}] {t}")
                    print(f"       Tags: {tags}")
                    print(f"       Media: {media}")
                    print(f"       Source: {source}")
                    
                results_summary.append({
                    "query": q,
                    "count": len(items),
                    "items": titles,
                    "duplicates": duplicates
                })
        except Exception as e:
            print(f"ERROR on query '{q}': {e}")
            results_summary.append({
                "query": q,
                "count": 0,
                "error": str(e)
            })

    # Save summary as JSON for reporting
    with open("audit_18_results.json", "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
    print("\nSaved full audit to audit_18_results.json")

if __name__ == "__main__":
    audit()
