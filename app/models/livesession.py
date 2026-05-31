from sqlalchemy import Column, Integer,ForeignKey,String,DateTime
from app.core.database import Base

class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    scheduled_at = Column(DateTime)
    duration_minutes = Column(Integer)
    meeting_url = Column(String)
    replay_url = Column(String, nullable=True)