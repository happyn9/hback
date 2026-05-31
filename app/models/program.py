from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from sqlalchemy.orm import relationship

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    code = Column(String, unique=True, nullable=False)
    semester = Column(String)
    is_active = Column(Boolean, default=True)

    courses = relationship("Course", back_populates="program", cascade="all, delete-orphan")