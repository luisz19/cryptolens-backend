from fastapi import FastAPI
from app import auth
from app.routes import cryptos
from app.routes import recommendations
from app.routes import questionnaire
from app.database import Base, engine

app = FastAPI(title="CryptoLens API")

app.include_router(auth.router)
app.include_router(cryptos.router)
app.include_router(recommendations.router)
app.include_router(questionnaire.router)

# Dev only: cria tabelas automaticamente no startup
@app.on_event("startup")
def on_startup_create_tables():
	from app import models
	Base.metadata.create_all(bind=engine)
