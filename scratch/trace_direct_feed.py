import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.api.feed import get_feed

print("[1] Opening DB session...", flush=True)
db = SessionLocal()
print("[2] DB session opened", flush=True)

print("[3] Calling get_feed directly...", flush=True)
async def run():
    res = await get_feed(q="Different types of bricks for a house", page_size=20, db=db)
    print(f"[4] Returned res items: {len(res.items)}", flush=True)

asyncio.run(run())
db.close()
print("[5] Done", flush=True)

