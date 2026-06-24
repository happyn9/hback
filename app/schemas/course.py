from pydantic import BaseModel
from typing import List, Optional

from pydantic import BaseModel
from typing import List, Optional

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_premium: bool = True
    order_index: int = 0
    tags: List[str] = []
    image_url: Optional[str] = None
    daily_price: float = 0
    weekly_price: float = 0
    monthly_price: float = 0
    program_id: int
    course_requirements: List[str] = []
    what_you_will_learn: List[str] = []

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int

    model_config = {"from_attributes": True}  

