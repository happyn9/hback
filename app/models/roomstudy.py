from sqlalchemy import Column, Integer,ForeignKey,func,DateTime
from app.core.database import Base


class StudyRoom(Base):
    __tablename__ = "study_rooms"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())


class StudyRoomMember(Base):
    __tablename__ = "study_room_members"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("study_rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))