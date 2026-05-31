from pydantic import BaseModel
from app.schemas.course import CourseCreate

class PinVerify(BaseModel):
    pin: str


class CourseWithPin(BaseModel):
    course: CourseCreate
    pin: str


class UpdatePinSchema(BaseModel):
    current_pin: str
    new_pin: str