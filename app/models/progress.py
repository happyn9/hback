from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey,Float,UniqueConstraint,Index
from sqlalchemy import Date
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    completed = Column(Boolean, default=False)
    progress_percent = Column(Float, default=0.0)  # 0 → 100
    last_position_seconds = Column(Integer, default=0)

    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson")

    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),
        Index('idx_user_lesson', 'user_id', 'lesson_id'),
    )

# ----------------- USER ACTIVITY -----------------
class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    minutes_spent = Column(Integer, default=0)

    user = relationship("User", back_populates="activity")



# ----------------- USER STREAK -----------------
class UserStreak(Base):
    __tablename__ = "user_streaks"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    last_active_date = Column(Date)
    streak_count = Column(Integer, default=1)

    user = relationship("User", back_populates="streaks")
