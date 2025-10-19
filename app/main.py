import os
from fastapi import FastAPI
from app import auth
from app.routes import cryptos
from app.routes import recommendations
from app.routes import questionnaire
from app.database import Base, engine, SessionLocal
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CryptoLens API")

app.include_router(auth.router)
app.include_router(cryptos.router)
app.include_router(recommendations.router)
app.include_router(questionnaire.router)

# Dev only: cria tabelas automaticamente no startup
@app.on_event("startup")
def on_startup_create_tables_and_seed():
	from app import models  # noqa: F401
	Base.metadata.create_all(bind=engine)

	# Seed opcional controlado por variável de ambiente
	seed_questions = os.getenv("SEED_QUESTIONS_ON_STARTUP", "false").lower() in ("1", "true", "yes")
	seed_cryptos = os.getenv("SEED_CRYPTOS_ON_STARTUP", "false").lower() in ("1", "true", "yes")
	if seed_questions or seed_cryptos:
		try:
			# Reutiliza o seeder existente
			from scripts.seed_db import seed_questions as _seed_questions, seed_cryptos as _seed_cryptos

			db = SessionLocal()
			try:
				if seed_questions:
					_seed_questions(db)
				if seed_cryptos:
					_seed_cryptos(db)
			finally:
				db.close()
		except Exception as e:
			# Não derruba a aplicação se o seed falhar
			print(f"[startup] Seed de perguntas não executado: {e}")
