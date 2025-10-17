from fastapi import FastAPI
from app import auth
from app.routes import cryptos

app = FastAPI(title="CryptoLens API")

app.include_router(auth.router)
app.include_router(cryptos.router)