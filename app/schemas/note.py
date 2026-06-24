from pydantic import BaseModel

class NoteCreate(BaseModel):
    lesson_id: int
    content: str

class NoteOut(NoteCreate):
    id: int

    model_config = {"from_attributes": True}  