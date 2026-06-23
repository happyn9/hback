from pydantic import BaseModel
from typing import Optional

class LessonBase(BaseModel):
    title: str
    type: str  # "video" | "pdf"
    video_url: Optional[str] = None

    duration_seconds: Optional[int] = None
    order_index: int = 1
    is_preview: bool = False

class LessonCreate(LessonBase):
    pass

class LessonOut(LessonBase):
    id: int

    class Config:
        orm_mode = True