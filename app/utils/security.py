from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Dict, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


load_dotenv()

SECRET_KEY: str = os.getenv("JWT_SECRET", "5bf4bae37304e632c10e8ad6c2436c5f")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
JWT_LEEWAY_SECONDS: int = int(os.getenv("JWT_LEEWAY_SECONDS", "60"))


def create_access_token(
	*,
	user_id: int,
	email: Optional[str] = None,
	expires_minutes: Optional[int] = None,
	extra: Optional[Dict[str, Any]] = None,
) -> str:
	"""Gera um JWT contendo o ID do usuário.

	Claims padrão:
	- sub: string com o ID do usuário
	- uid: inteiro com o ID (conveniência)
	- iat/exp: timestamps de emissão e expiração
	- email: opcional
	"""
	now = datetime.now(timezone.utc)
	exp_minutes = expires_minutes if expires_minutes is not None else ACCESS_TOKEN_EXPIRE_MINUTES
	exp = now + timedelta(minutes=exp_minutes)

	payload: Dict[str, Any] = {
		"sub": str(user_id),
		"uid": user_id,
		"iat": int(now.timestamp()),
		"exp": int(exp.timestamp()),
	}
	if email:
		payload["email"] = email
	if extra:
		payload.update(extra)

	token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
	if isinstance(token, bytes):
		token = token.decode("utf-8")
	return token


def verify_token(token: str) -> Dict[str, Any]:
	"""Valida e decodifica o JWT, retornando o payload.

	Lança HTTPException com códigos apropriados para expiração, assinatura inválida
	e token malformado.
	"""
	token = (token or "").strip().strip('"').strip()
	if not token:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token ausente")

	try:
		header = jwt.get_unverified_header(token)
		alg = header.get("alg")
		if alg and alg != ALGORITHM:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Algoritmo do token ({alg}) difere do esperado ({ALGORITHM})")
	except jwt.DecodeError:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token malformado (header)")

	try:
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM],
			leeway=JWT_LEEWAY_SECONDS,
		)
		return payload
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
	except jwt.InvalidSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Assinatura inválida")
	except jwt.DecodeError:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token malformado")
	except jwt.ImmatureSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não é válido ainda (nbf)")
	except jwt.InvalidIssuedAtError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token emitido no futuro (iat)")
	except jwt.InvalidAudienceError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Audiência inválida (aud)")
	except jwt.MissingRequiredClaimError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Claim obrigatória ausente: {getattr(e, 'claim', 'desconhecida')}")
	except jwt.InvalidTokenError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


bearer_scheme = HTTPBearer(auto_error=True)


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
	"""Extrai o token do header Authorization: Bearer <token> e retorna o payload válido."""
	return verify_token(credentials.credentials)


def decode_token_unverified(token: str) -> Dict[str, Any]:
	"""Decodifica o token sem verificar assinatura/expiração (uso diagnóstico)."""
	token = (token or "").strip().strip('"').strip()
	if not token:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token ausente")
	try:
		payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
		return payload
	except Exception:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token não pôde ser decodificado")


def get_user_id_from_payload(payload: Dict[str, Any]) -> int:
	"""Obtém o ID do usuário do payload (uid preferencialmente, depois sub)."""
	uid = payload.get("uid")
	if isinstance(uid, int):
		return uid
	sub = payload.get("sub")
	try:
		return int(sub)
	except (TypeError, ValueError):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem identificador de usuário")

