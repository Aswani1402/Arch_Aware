from app.core.database import engine, Base, SessionLocal
from app.models.models import *
from app.db.auto_migrate import auto_migrate
from app.db.seed_data import seed_database

def init_db():
    print("Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    print("Ensuring all table columns are migrated...")
    auto_migrate()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
