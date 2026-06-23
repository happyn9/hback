from fastapi import Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import desc

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.core.security import verify_pin

from app.models.user import User
from app.models.subscription import UserSubscription
from app.models.lesson import Lesson
from app.models.chapter import Chapter
from app.models.lesson_purchase import LessonPurchase
from app.models.course_purchase import CoursePurchase


# ================= DATABASE =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= AUTH =================
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, payload["user_id"])

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ================= SUBSCRIPTION =================
def has_active_subscription(user_id: int, db: Session):
    today = date.today()

    return (
        db.query(UserSubscription)
        .filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active.is_(True),
            UserSubscription.end_date >= today
        )
        .order_by(desc(UserSubscription.end_date))
        .first()
    )


# ================= LESSON ACCESS =================
def can_access_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lesson = db.get(Lesson, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if not lesson.is_premium:
        return lesson

    lesson_purchase = db.query(LessonPurchase).filter_by(
        user_id=user.id,
        lesson_id=lesson.id
    ).first()

    if lesson_purchase:
        return lesson

    chapter = db.get(Chapter, lesson.chapter_id)

    course_purchase = db.query(CoursePurchase).filter_by(
        user_id=user.id,
        course_id=chapter.course_id
    ).first()

    if course_purchase:
        return lesson

    if has_active_subscription(user.id, db):
        return lesson

    raise HTTPException(
        status_code=403,
        detail="This lesson is premium. Please unlock it."
    )


# ================= ADMIN =================
def require_admin(user: User = Depends(get_current_user)):
    if not user.role or user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ================= ADMIN PIN =================
def require_admin_pin(
    pin: str = Query(...),
    admin: User = Depends(require_admin)
):
    # Si aucun PIN n'est défini
    if not admin.pin_hash:
        expected_pin = "1234"

        if pin != expected_pin:
            raise HTTPException(
                status_code=403,
                detail="Invalid PIN"
            )

        return admin

    # Vérification du PIN enregistré
    if not verify_pin(pin, admin.pin_hash):
        raise HTTPException(
            status_code=403,
            detail="Invalid PIN"
        )

    return admin
