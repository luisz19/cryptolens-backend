# Cryptolens Backend

API backend em FastAPI com MySQL e suporte a autenticação JWT e previsão de criptomoedas (pipelines de ML). Este guia cobre instalação, configuração e execução local.

## Requisitos

- Python 3.10+
- MySQL 8.x
- Git (opcional)

## 1) Clonar e acessar o projeto

```bash
git clone <seu-fork-ou-URL> cryptolens-backend
cd cryptolens-backend
```

Se você já está nesta pasta, pode pular.

## 2) Ambiente virtual e dependências

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

Principais libs:
- fastapi, uvicorn: API e servidor
- SQLAlchemy, alembic: ORM e migrações
- mysql-connector-python: driver MySQL (síncrono)
- python-jose, passlib[bcrypt]: JWT e hashing de senha
- python-dotenv: variáveis de ambiente
- numpy, pandas, scikit-learn, joblib: ML básico

## 3) Configuração do .env

Crie um arquivo `.env` na raiz com:

```env
DATABASE_URL="mysql+pymysql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>"
```

## 4) Banco de dados MySQL

Crie o banco de dados:

```sql
CREATE DATABASE IF NOT EXISTS crypto_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

### Usando Docker (opcional)

```bash
docker run -d --name mysql8 \
	-e MYSQL_ROOT_PASSWORD=senha \
	-e MYSQL_DATABASE=crypto_db \
	-p 3306:3306 \
	mysql:8
```

## 5) Rodar a API

Assegure-se de ter um `app/main.py` com a aplicação FastAPI e as rotas montadas. Então:

```bash
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs

## 6) Estrutura básica sugerida

```
app/
	main.py
	database.py
	models.py
	schemas.py
	routes/
	services/
	utils/
	docs/http/
```

## 7) Dicas

- Se precisar async, troque o driver para `asyncmy` e adapte a criação de engine/Session.
- Use `JWT_SECRET` forte (32+ chars). Em produção, configure via variáveis de ambiente do sistema/contêiner.
- Ative logs SQL apenas em desenvolvimento (`SQLALCHEMY_ECHO=true`).

---

Qualquer dúvida, abra uma issue ou peça por um template de `database.py` e rotas de auth que já retornam o ID do usuário no token.