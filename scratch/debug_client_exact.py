import sys, os, time
sys.path.insert(0, 'backend')
sys.path.insert(0, '.')

from app.core.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
from pathlib import Path
from app.db.seed_data import seed_database
import app.models.models
from app.main import app
from fastapi.testclient import TestClient

t_dir = tempfile.mkdtemp()
t_db = Path(t_dir) / 'test.db'
engine = create_engine(f'sqlite:///{t_db.as_posix()}')
TestingSessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = TestingSessionLocal()
seed_database(db)

def override_get_db():
    yield db

app.dependency_overrides[get_db] = override_get_db

print("Starting TestClient...", flush=True)
client = TestClient(app)
print("Client started", flush=True)

query = "Different types of bricks for a house"
print(f"Calling client.get for '{query}'...", flush=True)
t0 = time.time()
resp = client.get("/api/feed", params={"q": query, "page_size": 20})
print(f"Status: {resp.status_code} in {time.time()-t0:.2f}s", flush=True)
data = resp.json()
items = data.get("items", [])
print(f"Items: {len(items)}", flush=True)
db.close()

