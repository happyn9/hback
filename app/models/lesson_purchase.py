from sqlalchemy import Column, Integer, ForeignKey, Date
from app.core.database import Base

class LessonPurchase(Base):
    __tablename__ = "lesson_purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    purchased_at = Column(Date)
