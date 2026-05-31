from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from app.core.database import Base
from sqlalchemy.orm import relationship

# ----------------- LESSON -----------------
class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    type = Column(String, nullable=False, default="video")  # video | pdf | quiz

    video_url = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    order_index = Column(Integer, default=1)

    is_preview = Column(Boolean, default=False)
    chapter = relationship("Chapter", back_populates="lessons")