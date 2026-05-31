from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Course, Lesson, Chapter
from app.schemas.course import CourseCreate, CourseOut
from app.schemas.chapter import ChapterOut
from app.dependencies import get_current_user
from app.models.progress import UserLessonProgress

router = APIRouter(prefix="/courses", tags=["Courses"])

# ---------------- CREATE COURSE ----------------
@router.post("/", response_model=CourseOut)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

# ---------------- GET ALL COURSES ----------------
@router.get("/", response_model=List[CourseOut])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

# ---------------- GET COURSE BY ID ----------------
@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    chapters = (
        db.query(Chapter)
        .filter(Chapter.course_id == course_id)
        .order_by(Chapter.order_index)
        .all()
    )

    result = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "image_url": course.image_url,
        "monthly_price": course.monthly_price,
        "course_requirements": course.course_requirements,
        "what_you_will_learn": course.what_you_will_learn,
        "chapters": []
    }


    for chapter in chapters:
        lessons = (
            db.query(Lesson)
            .filter(Lesson.chapter_id == chapter.id)
            .order_by(Lesson.order_index)
            .all()
        )

        result["chapters"].append({
            "id": chapter.id,
            "title": chapter.title,
            "lessons": [
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "is_preview": lesson.is_preview,
                }
                for lesson in lessons
            ]
        })

    return result
# ---------------- GET COURSE STATS ----------------
@router.get("/{course_id}/stats")
def course_stats(course_id: int, db: Session = Depends(get_db)):
    # ✅ Join Lesson avec Chapter pour accéder à course_id
    lessons = (
        db.query(Lesson)
        .join(Chapter)
        .filter(Chapter.course_id == course_id)
        .all()
    )

    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()

    total_duration = sum(lesson.duration_seconds or 0 for lesson in lessons)

    return {
        "course_id": course_id,
        "total_lessons": len(lessons),
        "total_chapters": len(chapters),
        "total_video_hours": round(total_duration / 3600, 2),
    }

# ---------------- GET PREMIUM COURSES ----------------
@router.get("/premium")
def get_premium_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.is_premium == True).all()
    return courses

# ---------------- GET CHAPTERS OF A COURSE ----------------
@router.get("/{course_id}/chapters", response_model=List[ChapterOut])
def get_course_chapters(course_id: int, db: Session = Depends(get_db)):
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    return chapters



@router.get("/{course_id}/current-lesson")
def get_current_lesson(course_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    # 1️⃣ Vérifier que le cours existe
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # 2️⃣ Chercher première lesson non complétée
    progress = (
        db.query(UserLessonProgress)
        .join(Lesson)
        .filter(
            UserLessonProgress.user_id == current_user.id,
            Chapter.course_id == course_id,
            UserLessonProgress.completed == False
        )
        .order_by(Lesson.order_index)
        .first()
    )

    if progress:
        return progress.lesson

    # 3️⃣ Sinon retourner première lesson du cours
    first_lesson = (
        db.query(Lesson)
        .join(Chapter)
        .filter(Chapter.course_id == course_id)
        .order_by(Chapter.order_index, Lesson.order_index)
        .first()
    )

    return first_lesson


@router.get("/{course_id}/progress")
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    total_lessons = db.query(Lesson)\
        .filter(Chapter.course_id == course_id)\
        .count()

    completed_lessons = (
        db.query(UserLessonProgress)
        .join(Lesson)
        .filter(
            UserLessonProgress.user_id == current_user.id,
            Chapter.course_id == course_id,
            UserLessonProgress.completed == True
        )
        .count()
    )

    percent = 0
    if total_lessons > 0:
        percent = round((completed_lessons / total_lessons) * 100, 2)

    return {
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "progress_percent": percent
    }

@router.get("/{course_id}/chapters-with-progress")
def get_chapters_with_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    chapters = (
        db.query(Chapter)
        .filter(Chapter.course_id == course_id)
        .order_by(Chapter.order_index)
        .all()
    )

    result = []

    for chapter in chapters:
        lessons = (
            db.query(Lesson)
            .filter(Lesson.chapter_id == chapter.id)
            .order_by(Lesson.order_index)
            .all()
        )

        lesson_data = []

        for lesson in lessons:
            progress = (
                db.query(UserLessonProgress)
                .filter(
                    UserLessonProgress.user_id == current_user.id,
                    UserLessonProgress.lesson_id == lesson.id
                )
                .first()
            )

            lesson_data.append({
                "id": lesson.id,
                "title": lesson.title,
                "completed": progress.completed if progress else False,
                "progress_percent": progress.progress_percent if progress else 0
            })

        result.append({
            "chapter_id": chapter.id,
            "chapter_title": chapter.title,
            "lessons": lesson_data
        })

    return result