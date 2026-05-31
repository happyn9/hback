from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Chapter
from app.schemas.chapter import ChapterCreate, ChapterOut

router = APIRouter(prefix="/chapters", tags=["Chapters"])


@router.post("/", response_model=ChapterOut)
def create_chapter(chapter: ChapterCreate, db: Session = Depends(get_db)):
    new_chapter = Chapter(**chapter.dict())
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    return new_chapter

