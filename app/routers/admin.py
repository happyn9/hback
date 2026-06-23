from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import require_admin
from app.core.security import verify_pin
from app.schemas.pinschema import UpdatePinSchema
from app.core.security import hash_pin
from app.schemas.pinschema import PinVerify,CourseWithPin

from app.models.course import Course
from app.models.chapter import Chapter
from app.models.program import Program
from app.models.lesson import Lesson

from app.schemas.course import CourseCreate, CourseOut
from app.schemas.chapter import ChapterCreate, ChapterOut
from app.schemas.program import ProgramCreate, ProgramOut
from app.schemas.lesson import LessonCreate, LessonOut

router = APIRouter(prefix="/admin", tags=["Admin"])

# =========================
# PROGRAM
# =========================
@router.post(
    "/programs",
    response_model=ProgramOut
)
def create_program(
    program: ProgramCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    # CHECK IF CODE EXISTS
    existing_program = db.query(Program).filter(
        Program.code == program.code
    ).first()

    if existing_program:
        raise HTTPException(
            status_code=400,
            detail="Program code already exists"
        )

    new_program = Program(
        **program.model_dump()
    )

    db.add(new_program)
    db.commit()
    db.refresh(new_program)

    return new_program

# =========================
# COURSE (PIN PROTECTED)
# =========================
@router.post(
    "/courses",
    response_model=CourseOut
)
def create_course(
    data: CourseWithPin,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    if not admin.pin_hash:
        if data.pin != "1234":
         raise HTTPException(
            status_code=403,
            detail="Invalid PIN"
         )
    else:
       if not verify_pin(
         data.pin,
         admin.pin_hash
       ):
       
        raise HTTPException(
            status_code=403,
            detail="Invalid PIN"
        )

    new_course = Course(
     **data.course.model_dump()
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course

# =========================
# CHAPTER
# =========================
@router.post("/courses/{course_id}/chapters", response_model=ChapterOut)
def add_chapter(
    course_id: int,
    chapter: ChapterCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_chapter = Chapter(**chapter.dict(), course_id=course_id)
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    return new_chapter


# =========================
# LESSON
# =========================
@router.post("/chapters/{chapter_id}/lessons", response_model=LessonOut)
def add_lesson(
    chapter_id: int,
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    new_lesson = Lesson(**lesson.dict(), chapter_id=chapter_id)
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson


# =========================
# VERIFY PIN (OPTIONAL DEBUG ENDPOINT)
# =========================
@router.post("/verify-pin")
def verify_admin_pin(
    data: PinVerify,
    admin=Depends(require_admin)
):

    if not admin.pin_hash:
        raise HTTPException(
            status_code=400,
            detail="PIN not set"
        )

    if not verify_pin(
        data.pin,
        admin.pin_hash
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid PIN"
        )

    return {
        "message": "PIN verified"
    }


# =========================
# UPDATE ADMIN PIN
# =========================
@router.put("/update-pin")
def update_admin_pin(
    data: UpdatePinSchema,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    # FIRST TIME SETUP
    if not admin.pin_hash:

        admin.pin_hash = hash_pin(
            data.new_pin
        )

        db.commit()

        return {
            "message": "PIN created"
        }

    # VERIFY OLD PIN
    if not verify_pin(
        data.current_pin,
        admin.pin_hash
    ):
        raise HTTPException(
            status_code=403,
            detail="Current PIN incorrect"
        )

    # UPDATE
    admin.pin_hash = hash_pin(
        data.new_pin
    )

    db.commit()

    return {
        "message": "PIN updated"
    }

@router.get("/programs", response_model=list[ProgramOut])
def get_programs(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return db.query(Program).all()

@router.get("/courses", response_model=list[CourseOut])
def get_courses(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return db.query(Course).all()

@router.get("/chapters", response_model=list[ChapterOut])
def get_chapters(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return db.query(Chapter).all()