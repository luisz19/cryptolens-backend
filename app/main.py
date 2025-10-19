import os
from fastapi import FastAPI
from app import auth
from app.routes import cryptos
from app.routes import recommendations
from app.routes import questionnaire
from dotenv import load_dotenv

app = FastAPI(title="CryptoLens API")

app.include_router(auth.router)
app.include_router(cryptos.router)
app.include_router(recommendations.router)
app.include_router(questionnaire.router)

load_dotenv()
