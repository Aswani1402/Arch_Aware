import sys
sys.path.insert(0, 'backend')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.get('/api/feed?q=Kota+stone')
assert resp.status_code == 200
items = resp.json().get('items', [])
print('TestClient Feed Kota Stone items:', len(items))
if items:
    print('Item 0:', items[0].get('title'))
    print('Provenance:', items[0].get('provenance'))
    print('Relevance tier:', items[0].get('inspiration_relevance_tier'))
    print('Media status:', items[0].get('media_status'))

