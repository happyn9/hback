from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.quiz import QuizChoice
from app.schemas.quiz import QuizAnswer

router = APIRouter(tags=["Quiz"])

@router.post("/submit")
def submit_quiz(answers: list[QuizAnswer], db: Session = Depends(get_db), user=Depends(get_current_user)):
    score = 0

    for answer in answers:
        choice = db.query(QuizChoice).get(answer.choice_id)
        if choice and choice.is_correct:
            score += 1

    return {
        "score": score,
        "total": len(answers)
    }
