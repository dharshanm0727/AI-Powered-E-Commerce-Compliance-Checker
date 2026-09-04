from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Database Engine with automatic SQLite fallback for local development
db_url = settings.DATABASE_URL
if "sqlite" in db_url:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        # Test connection
        with engine.connect() as conn:
            pass
    except Exception:
        # Fallback to local SQLite if Postgres is not running locally
        sqlite_url = "sqlite:///./compliance_db.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
