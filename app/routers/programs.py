from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Program
from app.schemas.program import ProgramCreate, ProgramOut

router = APIRouter(tags=["Programs"])

@router.post("/", response_model=ProgramOut)
def create_program(program: ProgramCreate, db: Session = Depends(get_db)):
    new_program = Program(**program.dict())
    db.add(new_program)
    db.commit()
    db.refresh(new_program)
    return new_program




