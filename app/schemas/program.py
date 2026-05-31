from pydantic import BaseModel
from typing import Optional

class ProgramBase(BaseModel):
    title: str
    code: str 
    description: Optional[str] = None

class ProgramCreate(ProgramBase):
    pass

class ProgramOut(ProgramBase):
    id: int

    class Config:
        orm_mode = True
