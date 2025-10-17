from sqlalchemy.orm import Session
from app import models

def classify_risk(total_score: int, max_score: int) -> models.RiskLevel:
	pct = total_score / max_score if max_score else 0
	if pct < 0.4:
		return models.RiskLevel.baixo
	if pct < 0.7:
		return models.RiskLevel.moderado
	return models.RiskLevel.alto


def submit_questionnaire(db: Session, user_id: int, answers: list[dict]) -> models.QuestionnaireSubmission:

	questions = db.query(models.Questions).all()
	opts_by_q = {q.id: {opt.value: opt for opt in q.options} for q in questions}

	total_score = 0
	max_score = len(questions) * 3 

	submission = models.QuestionnaireSubmission(
		user_id=user_id,
		total_score=0,
		max_score=max_score,
		risk_level=models.RiskLevel.baixo,
	)
	db.add(submission)
	db.flush()

	for ans in answers:
		qid = ans.get("question_id")
		sel_val = ans.get("selected_value")
		opt_id = ans.get("selected_option_id")
		opt = None
		if opt_id is not None:
			opt = db.query(models.QuestionOption).get(opt_id)
		elif sel_val is not None:
			opt = opts_by_q.get(qid, {}).get(sel_val)
		if not opt:
			score = 0
			final_value = sel_val or ""
			final_opt_id = None
		else:
			score = opt.score
			final_value = opt.value
			final_opt_id = opt.id
		total_score += score
		db.add(models.UserAnswer(
			submission_id=submission.id,
			user_id=user_id,
			question_id=qid,
			option_id=final_opt_id,
			selected_value=final_value,
			score=score,
		))

	risk = classify_risk(total_score, max_score)
	submission.total_score = total_score
	submission.risk_level = risk
	db.add(submission)

	user = db.query(models.User).get(user_id)
	if user:
		user.risk_profile = risk.value
		db.add(user)

	db.commit()
	db.refresh(submission)
	return submission


def update_questionnaire_submission(db: Session, submission_id: int, user_id: int, answers: list[dict]) -> models.QuestionnaireSubmission:
	submission = db.query(models.QuestionnaireSubmission).get(submission_id)
	if not submission:
		raise ValueError("Submission not found")

	db.query(models.UserAnswer).filter(models.UserAnswer.submission_id == submission_id).delete()
	db.flush()

	questions = db.query(models.Questions).all()
	opts_by_q = {q.id: {opt.value: opt for opt in q.options} for q in questions}
	total_score = 0
	max_score = len(questions) * 3

	for ans in answers:
		qid = ans.get("question_id")
		sel_val = ans.get("selected_value")
		opt_id = ans.get("selected_option_id")
		opt = None
		if opt_id is not None:
			opt = db.query(models.QuestionOption).get(opt_id)
		elif sel_val is not None:
			opt = opts_by_q.get(qid, {}).get(sel_val)
		score = opt.score if opt else 0
		total_score += score
		db.add(models.UserAnswer(
			submission_id=submission_id,
			user_id=user_id,
			question_id=qid,
			option_id=(opt.id if opt else None),
			selected_value=(opt.value if opt else (sel_val or "")),
			score=score,
		))

	risk = classify_risk(total_score, max_score)
	submission.total_score = total_score
	submission.max_score = max_score
	submission.risk_level = risk
	db.add(submission)
	user = db.query(models.User).get(user_id)
	if user:
		user.risk_profile = risk.value
		db.add(user)
	db.commit()
	db.refresh(submission)
	return submission
