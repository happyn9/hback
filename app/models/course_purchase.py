from sqlalchemy import Column, Integer, ForeignKey, Date
from app.core.database import Base




class CoursePurchase(Base):
    __tablename__ = "course_purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    purchased_at = Column(Date)

