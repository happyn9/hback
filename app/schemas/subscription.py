# app/schemas/subscription.py
from pydantic import BaseModel
from datetime import date
from typing import List

class SubscriptionOut(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: date
    end_date: date

    class Config:
        orm_mode = True

class SubscribeCoursesIn(BaseModel):
    course_ids: List[int]
    billing: str

class MultipleSubscribeIn(BaseModel):
    subscription_ids: List[int]