from pydantic import BaseModel
from typing import List

class OnboardingCompleteSchema(BaseModel):
    reason: List[str]
    program: str
    likes: List[str]
