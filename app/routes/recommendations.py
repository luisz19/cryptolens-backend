from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/")
def get_recommendations(db: Session = Depends(get_db)):
    recommendations = db.query(models.Recommendation).all()
    return recommendations

@router.get("/{recommendation_id}")
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = db.query(models.Recommendation).filter(models.Recommendation.id == recommendation_id).first()
    return recommendation

@router.post("/")
def create_recommendation(recommendation: schemas.RecommendationCreate, db: Session = Depends(get_db)):
    db_recommendation = models.Recommendation(**recommendation.dict())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

@router.patch("/{recommendation_id}")
def update_recommendation(risk_level: schemas.RiskLevelUpdate, recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = db.query(models.Recommendation).filter(models.Recommendation.id == recommendation_id).first()
    if recommendation:
        recommendation.risk_level = risk_level.risk_level
        db.commit()
        db.refresh(recommendation)
        return recommendation
    return {"error": "Recommendation not found"}

    