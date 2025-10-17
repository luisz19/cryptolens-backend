from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt, datetime, os
from dotenv import load_dotenv

from app import models, schemas
from app.database import SessionLocal

load_dotenv() # TROCAR DEPOIS

router = APIRouter(prefix="/auth", tags=["Auth"])
SECRET_KEY = os.getenv("JWT_SECRET", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(user_id: int, email: str | None = None):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "uid": user_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if email:
        payload["email"] = email
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
   
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token(new_user.id, email=new_user.email)

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

    token = create_token(user_db.id, email=user_db.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_db.id,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

@router.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return schemas.UserResponse.from_orm(user)

