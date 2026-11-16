import os
import json
import urllib.request
import urllib.parse
from app.core.config import settings

def search_yt(query, max_results=3):
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        print("No YOUTUBE_API_KEY configured")
        return []
    
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={urllib.parse.quote(query)}&type=video&videoEmbeddable=true&maxResults={max_results}&key={api_key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = []
            for item in data.get("items", []):
                vid = item["id"]["videoId"]
                snip = item["snippet"]
                items.append({
                    "videoId": vid,
                    "title": snip["title"],
                    "channel": snip["channelTitle"],
                    "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                })
            return items
    except Exception as e:
        print(f"Error searching YouTube for '{query}': {e}")
        return []

if __name__ == "__main__":
    test_queries = [
        "Small bathroom renovation before and after",
        "Modular kitchen renovation storage walkthrough",
        "Screws and bolts types building construction fasteners",
        "Modular electrical switches and switchboards modern house",
        "Exterior facade lighting outdoor architectural illumination",
        "Rammed earth wall construction techniques",
        "Wood look porcelain floor tiles installation",
        "Civil construction site walkthrough foundation to finish"
    ]
    for q in test_queries:
        print(f"\n--- Searching YouTube: '{q}' ---")
        res = search_yt(q, max_results=2)
        for r in res:
            print(f"  [{r['videoId']}] {r['title']} ({r['channel']})")
