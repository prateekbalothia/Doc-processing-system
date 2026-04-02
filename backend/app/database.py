from sqlalchemy import create_engine
from sqlalchemy.orm import session, sessionmaker, declarative_base
from tenacity import retry, stop_after_attempt, wait_fixed

DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"

@retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
def get_engine():
    return create_engine(DATABASE_URL)

engine = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()