from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.course import Course
from app.schemas.course import CourseOut  # ton Pydantic

router = APIRouter(prefix="/premium")

@router.get("/courses", response_model=List[CourseOut])
def get_premium_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.is_premium == True).all()
    return courses  # FastAPI convertira automatiquement les objets SQLAlchemy en JSON grâce à orm_mode
