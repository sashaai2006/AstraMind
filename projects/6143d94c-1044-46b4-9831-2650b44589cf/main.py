from fastapi import FastAPI
from sqlalchemy import create_engine, engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the database tables
from . import models
Base.metadata.create_all(engine)
