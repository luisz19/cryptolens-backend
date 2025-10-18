from app.utils.security import (
    get_user_id_from_payload,
    require_auth,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import load_dotenv

from app import models, schemas
from app.database import SessionLocal

load_dotenv() # TROCAR DEPOIS

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
   
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(user_id=new_user.id, email=new_user.email)

    return {
        "message": "Usuário criado com sucesso!", 
        "access_token": token, 
        "token_type": "bearer",
        "user_id": new_user.id,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if not user_db or not pwd_context.verify(user.password, user_db.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_access_token(user_id=user_db.id, email=user_db.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_db.id,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

@router.put("/user/{user_id}", response_model=schemas.UserResponse)
def update_user_by_id(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    data = payload.model_dump(exclude_unset=True)

    new_email = data.get("email")
    if new_email and new_email != user.email:
        exists = db.query(models.User).filter(models.User.email == new_email, models.User.id != user.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    new_password = data.get("password")
    if new_password:
        data["password"] = pwd_context.hash(new_password)

    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserResponse.from_orm(user)

@router.delete("/user/{user_id}")
def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(user)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}

@router.get("/me")
def me(payload: dict = Depends(require_auth), db: Session = Depends(get_db)):
    user_id = get_user_id_from_payload(payload)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"user_id": user_id,
            "email": user.email,
            "name": user.name,
            "risk_profile": user.risk_profile,
    }

