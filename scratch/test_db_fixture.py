import sys
from pathlib import Path
sys.path.insert(0, "backend")
sys.path.insert(0, ".")
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app as application
from app.core.database import Base, get_db
import app.models.models
from app.db.seed_data import seed_database
from app.models.models import SavedItem
from app.core.security import create_access_token

temp_dir = tempfile.mkdtemp(prefix="test_db_fix_")
db_path = Path(temp_dir) / "test.db"
test_url = f"sqlite:///{db_path.as_posix()}"

engine = create_engine(test_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
init_db_session = TestingSessionLocal()
seed_database(init_db_session)
init_db_session.close()

# Test overriding get_db
test_session = TestingSessionLocal()

def override_get_db():
    try:
        yield test_session
    finally:
        pass

application.dependency_overrides[get_db] = override_get_db

token = create_access_token(subject="architect@studio.com", role="user")
headers = {"Authorization": f"Bearer {token}"}

client = TestClient(application)
print("Sending save toggle request...")
res = client.post("/api/saved/toggle", json={"item_type": "reference", "reference_id": 999999, "project_collection": "Test"}, headers=headers)
print("Status code:", res.status_code)
print("Response JSON:", res.json())

# Check record in test DB
saved = test_session.query(SavedItem).filter_by(reference_id=999999).first()
print("Saved record found in test DB?", saved is not None)

# Clean up
application.dependency_overrides.clear()
test_session.close()
engine.dispose()
print("Test completed successfully without any hang!")
