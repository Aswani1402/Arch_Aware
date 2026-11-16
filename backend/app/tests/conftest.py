import os
import shutil
import tempfile
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
import app.models.models  # Ensure all model tables are registered in Base.metadata
from app.db.seed_data import seed_database
from app.main import app

# Create isolated session-scoped temporary file-based SQLite database
_TEST_TEMP_DIR = tempfile.mkdtemp(prefix="nivora_test_db_")
_TEST_DB_PATH = Path(_TEST_TEMP_DIR) / "test_architect_ai.db"
TEST_DATABASE_URL = f"sqlite:///{_TEST_DB_PATH.as_posix()}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import inspect
import asyncio

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async coroutine")

def pytest_pyfunc_call(pyfuncitem):
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        args = {arg: pyfuncitem.funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames if arg in pyfuncitem.funcargs}
        asyncio.run(pyfuncitem.obj(**args))
        return True

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    try:
        from app.db.seed_taxonomy_29 import sync_taxonomy_29
        sync_taxonomy_29(db)
        from reconcile_authentic_content import reconcile
        reconcile(db)
    except Exception as e:
        print(f"[conftest] Warning syncing test db: {e}")
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    shutil.rmtree(_TEST_TEMP_DIR, ignore_errors=True)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def isolate_test_database(db):
    """
    Guarantees that EVERY test client and API endpoint automatically routes database
    operations to the isolated transaction-rolled-back test session, protecting the
    development database from accidental writes.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_headers():
    from app.core.security import create_access_token
    token = create_access_token(subject="architect@studio.com", role="user")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    from app.core.security import create_access_token
    token = create_access_token(subject="admin@architect.ai", role="admin")
    return {"Authorization": f"Bearer {token}"}
