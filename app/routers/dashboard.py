# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.lesson import Lesson
from app.models.progress import UserLessonProgress, UserStreak
from typing import Dict
from datetime import datetime

router = APIRouter(tags=["Dashboard"])

@router.get("/summary")
def dashboard_summary(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renvoie le résumé de progression de l'utilisateur :
    - completed_lessons
    - total_lessons
    - progress_percent
    - streak_days
    """
    total = db.query(UserLessonProgress).filter_by(user_id=user.id).count()
    completed = db.query(UserLessonProgress).filter_by(user_id=user.id, completed=True).count()
    streak = db.query(UserStreak).filter_by(user_id=user.id).first()

    return {
        "completed_lessons": completed,
        "total_lessons": total,
        "progress_percent": round((completed / total * 100) if total else 0, 2),
        "streak_days": streak.streak_count if streak else 0
    }

@router.get("/my-courses")
def my_courses(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renvoie les cours de l'utilisateur avec chapters et lessons
    """
    courses = db.query(Course).options(joinedload(Course.chapters).joinedload(Chapter.lessons)).all()
    result = []

    for course in courses:
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "image_url": course.image_url,
            "monthly_price": course.monthly_price,
            "course_requirements": course.course_requirements,
            "what_you_will_learn": course.what_you_will_learn,
            "chapters": []
        }

        chapters = db.query(Chapter).filter(Chapter.course_id == course.id).order_by(Chapter.order_index).all()
        for chapter in chapters:
            lessons = db.query(Lesson).filter(Lesson.chapter_id == chapter.id).order_by(Lesson.order_index).all()
            lesson_list = []
            for lesson in lessons:
                progress = db.query(UserLessonProgress).filter_by(user_id=user.id, lesson_id=lesson.id).first()
                lesson_list.append({
                    "id": lesson.id,
                    "title": lesson.title,
                    "is_preview": lesson.is_preview,
                    "completed": progress.completed if progress else False
                })

            course_dict["chapters"].append({
                "id": chapter.id,
                "title": chapter.title,
                "lessons": lesson_list
            })

        result.append(course_dict)
    return result

@router.get("/schedule")
def my_schedule(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retourne un planning simplifié par jour de la semaine
    {
        "Mon": [{"time": "10:00", "class": "Lesson title"}],
        "Tue": [...]
    }
    """
    schedule: Dict[str, list] = {day: [] for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}

    # ✅ Join Lesson → Chapter pour accéder aux infos de cours
    lessons = db.query(Lesson).join(Chapter).all()

    for lesson in lessons:
        day = getattr(lesson, "scheduled_day", None)
        time = getattr(lesson, "scheduled_time", None)
        if day in schedule:
            schedule[day].append({
                "time": time or "TBD",
                "class": lesson.title
            })

    return schedule


from app.models.subscription import UserSubscription, Subscription
from datetime import date

@router.get("/my-courses-with-progress")
def my_courses_with_progress(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Récupère uniquement les cours auxquels l'utilisateur est abonné,
    avec progression par leçon.
    """

    # 1️⃣ Récupère les abonnements actifs
    active_subs = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.is_active == True,
        UserSubscription.start_date <= date.today(),
        UserSubscription.end_date >= date.today()
    ).all()

    if not active_subs:
        return []

    # 2️⃣ Récupère tous les IDs de Subscription
    subscription_ids = [sub.subscription_id for sub in active_subs]

    # 3️⃣ Récupère tous les cours liés à ces subscriptions
    subscribed_courses = db.query(Course).join(Subscription).filter(
        Subscription.id.in_(subscription_ids)
    ).options(
        joinedload(Course.chapters).joinedload(Chapter.lessons)
    ).all()

    # 4️⃣ Récupère la progression de l'utilisateur
    progress_list = db.query(UserLessonProgress).filter_by(user_id=user.id).all()
    progress_dict = {p.lesson_id: p for p in progress_list}

    # 5️⃣ Assemble le résultat
    result = []
    for course in subscribed_courses:
        course_dict = {
            "id": course.id,
            "title": course.title,
            "chapters": []
        }
        for chapter in course.chapters:
            lesson_data = []
            for lesson in chapter.lessons:
                lesson_progress = progress_dict.get(lesson.id)
                lesson_data.append({
                    "id": lesson.id,
                    "title": lesson.title,
                    "completed": lesson_progress.completed if lesson_progress else False
                })
            course_dict["chapters"].append({
                "id": chapter.id,
                "title": chapter.title,
                "lessons": lesson_data
            })
        result.append(course_dict)

    return result