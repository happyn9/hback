from pydantic import BaseModel

class ProgressSummary(BaseModel):
    completed_lessons: int
    total_lessons: int
    progress_percent: float
    streak_days: int


class LessonProgressUpdate(BaseModel):
    progress_percent: float
    last_position_seconds: int
    completed: bool = False