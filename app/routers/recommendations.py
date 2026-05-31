from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.program import Program
from app.dependencies import get_current_user, get_db
from app.models.course import Course
from app.schemas.onboarding import OnboardingCompleteSchema
import random
from datetime import datetime

router = APIRouter(tags=["Recommendations"])

# 🎯 Messages inspirants par programme
MESSAGES = {
    "se": [
        "Every great software starts with one line of code.",
        "Consistency beats talent in software engineering.",
        "Debugging is the path to mastery — keep going!"
    ],
    "cs": [
        "Computer science is the science of problem solving.",
        "Learn, code, repeat — greatness awaits.",
        "Algorithms build the foundation of the future."
    ],
    "net": [
        "Networks connect the world — and your future.",
        "The world runs on connections — understand them.",
        "Secure, scale, succeed — start learning now!"
    ],
    "af": [
        "Understanding numbers is understanding power.",
        "Finance is the language of business — speak it well.",
        "Balance sheets tell stories — decode them!"
    ],
}

@router.get("/home")
def home_recommendation(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    academic = user.academic or {}
    onboarding = user.onboarding or {}

    program_code = academic.get("program")
    likes = onboarding.get("likes", [])

    # 🛡️ SAFE VALUES
    safe_program = program_code.upper() if program_code else None
    safe_name = user.name or "Learner"

    # 📢 Message inspirant
    messages = MESSAGES.get(program_code, ["Learning something new every day changes everything."])
    message = random.choice(messages)

    # 📘 Recommandation de cours
    course = None
    if program_code:  # ⚠️ Ne chercher que si on a un programme
        query = (
            db.query(Course)
            .join(Course.program)
            .filter(Program.code == program_code)
        )

        if likes:
            query = query.filter(or_(*[Course.tags.contains([tag]) for tag in likes]))

        course = query.order_by(Course.order_index).first()

    return {
        "timestamp": datetime.utcnow(),
        "message": message,
        "program": program_code,
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "is_premium": course.is_premium,
        } if course else None,
        "encouragement": (
            f"Keep pushing, {safe_name}! "
            f"Explore {safe_program if safe_program else 'your learning path'} "
            f"and master your skills!"
        ),
    }


@router.post("/home")
def save_onboarding_and_prepare_reco(
    payload: OnboardingCompleteSchema,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 🔹 Sauvegarde onboarding
    user.onboarding = {
        "reason": payload.reason,
        "likes": payload.likes,
    }

    user.academic = {
        "program": payload.program
    }

    # 🔥 IMPORTANT
    user.onboarding_completed = True

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "ok", "onboarding_completed": user.onboarding_completed}
