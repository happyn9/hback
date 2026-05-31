from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship

# ----------------- CHAPTER -----------------
class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    course = relationship("Course", back_populates="chapters")
    lessons = relationship("Lesson",back_populates="chapter",cascade="all, delete-orphan",order_by="Lesson.order_index")
