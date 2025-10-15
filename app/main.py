from fastapi import FastAPI
from app import auth

app = FastAPI(title="CryptoLens API")

app.include_router(auth.router)
