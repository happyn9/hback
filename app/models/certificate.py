from sqlalchemy import Column, Integer,ForeignKey,String,DateTime,func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    issued_at = Column(DateTime, server_default=func.now())
    certificate_url = Column(String)

    user = relationship("User")
    course = relationship("Course")