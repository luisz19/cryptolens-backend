from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas
from app.services.risk_service import submit_questionnaire, update_questionnaire_submission
from app import models
from app.utils.security import require_auth, get_user_id_from_payload

router = APIRouter(prefix="/questionnaire", tags=["Questionnaire"])

@router.get("/questions", response_model=list[schemas.Question])
def list_questions(db: Session = Depends(get_db), _=Depends(require_auth)):
    questions = db.query(models.Questions).all()
    return questions

@router.post("/submit", response_model=schemas.QuestionnaireResult)
def submit(data: schemas.QuestionnaireSubmitIn, db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    if auth_user_id != data.user_id:
        raise HTTPException(status_code=403, detail="Token não corresponde ao usuário informado")
    user = db.query(models.User).get(data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    submission = submit_questionnaire(db, data.user_id, [a.model_dump() for a in data.answers])
    return schemas.QuestionnaireResult(
        submission_id=submission.id,
        total_score=submission.total_score,
        max_score=submission.max_score,
        risk_level=submission.risk_level.value,
    )

@router.get("/submission/", response_model=list[schemas.QuestionnaireResult])
def list_submissions(db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    submissions = db.query(models.QuestionnaireSubmission).filter(models.QuestionnaireSubmission.user_id == auth_user_id).all()
    return [
        schemas.QuestionnaireResult(
            submission_id=submission.id,
            total_score=submission.total_score,
            max_score=submission.max_score,
            risk_level=submission.risk_level.value,
        )
        for submission in submissions
    ]

@router.get("/answers/", response_model=list[schemas.UserAnswer])
def list_answers(db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    answers = db.query(models.UserAnswer).filter(models.UserAnswer.user_id == auth_user_id).all()
    return answers

@router.put("/submission/{submission_id}", response_model=schemas.QuestionnaireResult)
def update_submission(submission_id: int, data: schemas.QuestionnaireSubmitIn, db: Session = Depends(get_db), payload: dict = Depends(require_auth)):
    auth_user_id = get_user_id_from_payload(payload)
    if auth_user_id != data.user_id:
        raise HTTPException(status_code=403, detail="Token não corresponde ao usuário informado")
    submission = db.query(models.QuestionnaireSubmission).get(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    if submission.user_id != data.user_id:
        raise HTTPException(status_code=400, detail="Usuário não bate com a submissão")
    updated_submission = update_questionnaire_submission(db, submission_id, data.user_id, [a.model_dump() for a in data.answers])
    return schemas.QuestionnaireResult(
        submission_id=updated_submission.id,
        total_score=updated_submission.total_score,
        max_score=updated_submission.max_score,
        risk_level=updated_submission.risk_level.value,
    )

    
