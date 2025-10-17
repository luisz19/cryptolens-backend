from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/cryptos", tags=["Cryptos"])

@router.get("/", response_model=list[schemas.CryptoResponse])
def get_cryptos(db: Session = Depends(get_db)):
    cryptos = db.query(models.Cryptos).all()
    return cryptos

@router.post("/", response_model=schemas.CryptoResponse)
def create_crypto(crypto: schemas.CryptoCreate, db: Session = Depends(get_db)):
    new_crypto = models.Cryptos(
        name=crypto.name,
        symbol=crypto.symbol
    )
    db.add(new_crypto)
    db.commit()
    db.refresh(new_crypto)
    return new_crypto