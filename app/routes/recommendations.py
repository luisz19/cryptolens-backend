from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.utils.security import require_auth, get_user_id_from_payload

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

@router.get("/{recommendation_id}")
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

@router.patch("/{recommendation_id}")
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

    