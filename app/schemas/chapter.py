from pydantic import BaseModel


class ChapterBase(BaseModel):
    title: str
    order_index: int = 1

class ChapterCreate(ChapterBase):
    pass

class ChapterOut(ChapterBase):
    id: int

    model_config = {"from_attributes": True}  
