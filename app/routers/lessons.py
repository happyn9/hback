from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models import Lesson
from app.models.progress import UserLessonProgress
from app.schemas.lesson import LessonCreate, LessonOut
from app.schemas.progress import LessonProgressUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.post("/", response_model=LessonOut)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lesson.
    """
    new_lesson = Lesson(**lesson.dict())
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson


@router.post("/{lesson_id}/progress")
def update_lesson_progress(
    lesson_id: int,
    payload: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update or create user's progress for a specific lesson.
    """
    # Check if the lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get existing progress or create new
    progress = (
        db.query(UserLessonProgress)
        .filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.lesson_id == lesson_id
        )
        .first()
    )

    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(progress)

    # Update progress fields
    progress.progress_percent = payload.progress_percent
    progress.last_position_seconds = payload.last_position_seconds
    progress.completed = payload.completed

    if payload.completed:
        progress.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    return {"message": "Progress updated successfully"}


@router.get("/{lesson_id}/video")
def get_lesson_video(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve the video URL for a specific lesson.
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"video_url": lesson.video_url}