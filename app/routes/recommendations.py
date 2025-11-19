from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.utils.security import require_auth, get_user_id_from_payload
from app.ml.recommender import recommend_cryptos
import pandas as pd
import os


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/")
def get_recommendations(db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    recommendations = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.user_id == auth_user_id)
        .all()
    )
    return recommendations

@router.get("/id/{recommendation_id}")
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    recommendation = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.id == recommendation_id)
        .first()
    )
    if not recommendation or recommendation.user_id != auth_user_id:
        return {"error": "Recommendation not found"}
    return recommendation

@router.post("/")
def create_recommendation(recommendation: schemas.RecommendationCreate, db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    data = recommendation.dict()
    data["user_id"] = auth_user_id
    db_recommendation = models.Recommendation(**data)
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

@router.patch("/id/{recommendation_id}")
def update_recommendation(risk_level: schemas.RiskLevelUpdate, recommendation_id: int, db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    recommendation = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.id == recommendation_id)
        .first()
    )
    if not recommendation or recommendation.user_id != auth_user_id:
        return {"error": "Recommendation not found"}
    recommendation.risk_level = risk_level.risk_level
    db.commit()
    db.refresh(recommendation)
    return recommendation

def _resolve_risk_profile(risk_profile_param, body_obj, user_obj):
    if risk_profile_param is not None:
        return risk_profile_param.value if hasattr(risk_profile_param, "value") else str(risk_profile_param)
    if body_obj and body_obj.risk_profile is not None:
        rp = body_obj.risk_profile
        return rp.value if hasattr(rp, "value") else str(rp)
    if user_obj and user_obj.risk_profile:
        return user_obj.risk_profile
    return None

def _generate_dynamic_recommendations(db: Session, auth_user_id: int, effective_profile: str):
    csv_path = os.getenv("RECOMMENDER_CSV_PATH", "app/docs/dataframe_com_features.csv")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Arquivo CSV não encontrado em '{csv_path}'. Suba o arquivo ou ajuste RECOMMENDER_CSV_PATH.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao ler CSV: {e}")

    required_cols = ["network", "volatility_7", "symbol"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV precisa conter as colunas: {', '.join(missing)}.")

    try:
        registered = {c.symbol for c in db.query(models.Cryptos).all()}
        results = recommend_cryptos(effective_profile, df, allowed_symbols=registered)
    except KeyError as e:
        missing = str(e).strip("'\"")
        raise HTTPException(status_code=400, detail=f"Coluna de feature ausente no CSV: {missing}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao gerar recomendações: {e}")
    return results

@router.post("/recommender")
def run_recommender(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_auth),
    risk_profile: schemas.RiskLevelEnum | None = Query(default=None, description="Perfil de risco: baixo, moderado, alto"),
    body: schemas.RecommenderRequest | None = None,
):
    auth_user_id = get_user_id_from_payload(payload)
    user = db.query(models.User).get(auth_user_id)
    effective = _resolve_risk_profile(risk_profile, body, user)
    if effective not in {"baixo", "moderado", "alto"}:
        raise HTTPException(status_code=400, detail="risk_profile ausente ou inválido (use: baixo/moderado/alto)")
    results = _generate_dynamic_recommendations(db, auth_user_id, effective)
    return {"profile": effective, "recommendations": results}

@router.get("/recommender")
def get_recommender(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_auth),
    risk_profile: schemas.RiskLevelEnum | None = Query(default=None, description="Perfil de risco: baixo, moderado, alto"),
):
    auth_user_id = get_user_id_from_payload(payload)
    user = db.query(models.User).get(auth_user_id)
    effective = _resolve_risk_profile(risk_profile, None, user)
    if effective not in {"baixo", "moderado", "alto"}:
        raise HTTPException(status_code=400, detail="risk_profile ausente ou inválido (use: baixo/moderado/alto)")
    results = _generate_dynamic_recommendations(db, auth_user_id, effective)
    return {"profile": effective, "recommendations": results}