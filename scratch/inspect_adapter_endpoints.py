import re

with open('backend/app/services/discovery_adapters.py', 'r', encoding='utf-8') as f:
    text = f.read()

adapters = [
    'PinterestAdapter',
    'InstagramAdapter',
    'YouTubeAdapter',
    'RedditAdapter',
    'GoogleSearchAdapter',
    'GoogleShoppingAdapter',
    'GooglePlacesAdapter'
]

for adp in adapters:
    m = re.search(r'class ' + adp + r'\(', text)
    if m:
        start = m.start()
        # Find next class
        next_m = re.search(r'\nclass ', text[start+10:])
        end = start + 10 + next_m.start() if next_m else len(text)
        sub = text[start:end]
        urls = set(re.findall(r'https?://[^\s"\'\)]+', sub))
        
        # Check connector imports or calls
        connector_calls = set(re.findall(r'([A-Za-z0-9_]+service|[A-Za-z0-9_]+connector|[A-Za-z0-9_]+client)', sub, re.IGNORECASE))
        print(f"=== {adp} ===")
        print(f"  URLs: {urls}")
        print(f"  Connectors/Services mentioned: {[c for c in connector_calls if 'self' not in c]}")

