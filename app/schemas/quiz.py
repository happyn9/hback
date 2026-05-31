from pydantic import BaseModel

class QuizAnswer(BaseModel):
    quiz_id: int
    choice_id: int
