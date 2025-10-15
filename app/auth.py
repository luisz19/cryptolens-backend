from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt, datetime

from app import models, schemas
from app.database import SessionLocal

router = APIRouter(prefix="/auth", tags=["Auth"])
SECRET_KEY = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # TROCAR DEPOIS
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(user_id: int):
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
   
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuário criado com sucesso!"}

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if not user_db or not pwd_context.verify(user.password, user_db.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_token(user_db.id)
    return {"access_token": token, "token_type": "bearer"}
