import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal, Base, engine
from app import models

load_dotenv()

QUESTIONS = [
    {
        "text": "Qual o seu horizonte de investimento em criptomoedas?",
        "options": [
            {"value": "short", "label": "Curto prazo (até 6 meses)", "score": 1},
            {"value": "medium", "label": "Médio prazo (6 meses a 2 anos)", "score": 2},
            {"value": "long", "label": "Longo prazo (mais de 2 anos)", "score": 3},
        ],
    },
    {
        "text": "Se o valor cair 20% em uma semana, o que você faria?",
        "options": [
            {"value": "sell", "label": "Vender tudo imediatamente", "score": 1},
            {"value": "hold", "label": "Manter parte e observar", "score": 2},
            {"value": "buyMore", "label": "Comprar mais (aproveitar a queda)", "score": 3},
        ],
    },
    {
        "text": "Qual o seu nível de conhecimento sobre investimentos?",
        "options": [
            {"value": "beginner", "label": "Nenhum ou iniciante", "score": 1},
            {"value": "intermediate", "label": "Já invisto em outras classes", "score": 2},
            {"value": "advanced", "label": "Tenho experiência com cripto/trading", "score": 3},
        ],
    },
    {
        "text": "Qual é o seu principal objetivo com criptomoedas?",
        "options": [
            {"value": "protect", "label": "Proteger capital", "score": 1},
            {"value": "grow", "label": "Crescer gradualmente", "score": 2},
            {"value": "maximize", "label": "Máximo retorno possível", "score": 3},
        ],
    },
    {
        "text": "Qual percentual do patrimônio investiria em criptomoedas?",
        "options": [
            {"value": "upto10", "label": "Até 10%", "score": 1},
            {"value": "10to30", "label": "De 10% a 30%", "score": 2},
            {"value": "over30", "label": "Mais de 30%", "score": 3},
        ],
    },
]


def seed_questions(db: Session):
    # evita duplicar seeds: se já há perguntas, não faz nada
    has_any = db.query(models.Questions).first()
    if has_any:
        print("Questions already seeded. Skipping.")
        return

    for q in QUESTIONS:
        question = models.Questions(question_text=q["text"])
        db.add(question)
        db.flush()  # pega o ID
        for opt in q["options"]:
            db.add(models.QuestionOption(
                question_id=question.id,
                value=opt["value"],
                label=opt["label"],
                score=opt["score"],
            ))
    db.commit()
    print("Seeded questions and options.")


def main():
    # cria tabelas se não existirem (dev convenience)
    from app import models as _models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_questions(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
