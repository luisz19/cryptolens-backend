from fastapi import FastAPI
from app import auth
from app.routes import cryptos
from app.routes import recommendations

app = FastAPI(title="CryptoLens API")

app.include_router(auth.router)
app.include_router(cryptos.router)
app.include_router(recommendations.router)
