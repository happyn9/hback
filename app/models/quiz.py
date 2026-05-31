from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.lesson import Lesson

# ----------------- QUIZ -----------------
class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question = Column(String, nullable=False)

    lesson = relationship("Lesson", back_populates="quizzes")
    choices = relationship("QuizChoice", back_populates="quiz", cascade="all, delete-orphan")

class QuizChoice(Base):
    __tablename__ = "quiz_choices"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    choice = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)  # 0 / 1 remplacé par Boolean pour clarté

    quiz = relationship("Quiz", back_populates="choices")

# Ajouter la relation dans Lesson
Lesson.quizzes = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))

    question = Column(String)
    options = Column(JSON)
    correct_answer = Column(String)