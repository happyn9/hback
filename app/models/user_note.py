from sqlalchemy import Column, Integer,Text,ForeignKey,func,DateTime
from app.core.database import Base
from sqlalchemy.orm import relationship


# ----------------- USER NOTES -----------------
class UserNote(Base):
    __tablename__ = "user_notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="notes")
    lesson = relationship("Lesson")