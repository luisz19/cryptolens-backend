from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv() 

# print(os.getenv("DATABASE_URL"))

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
	"""Dependência do FastAPI para obter uma sessão de DB por request.
	Uso: def endpoint(db: Session = Depends(get_db))
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
