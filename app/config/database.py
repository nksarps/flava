from decouple import config

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = config('DB_URI')

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)
Base = declarative_base()

async def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(engine)