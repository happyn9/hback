from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.program import Program

PROGRAMS = [
    {
        "title": "Software Engineering",
        "description": "Programming, frontend, backend, and software architecture.",
        "code": "se",
        "semester": "All",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475",
    },
    {
        "title": "Computer Science",
        "description": "Algorithms, data structures, and computer fundamentals.",
        "code": "cs",
        "semester": "All",
        "image_url": "https://images.unsplash.com/photo-1517433456452-f9633a875f6f",
    },
    {
        "title": "English Tuition",
        "description": "Beginners, Intermediate, and Advanced.",
        "code": "eng",
        "semester": "All",
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644",
    },
    {
        "title": "Accounting & Finance",
        "description": "Finance, accounting, and business fundamentals.",
        "code": "af",
        "semester": "All",
        "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c",
    },
    {
        "title": "Networking",
        "description": "Networks, infrastructure, security, and systems.",
        "code": "net",
        "semester": "All",
        "image_url": "https://images.unsplash.com/photo-1526378722484-cc5c2cbb3f8b",
    },
]


def seed_programs():
    db: Session = SessionLocal()

    for p in PROGRAMS:
        exists = db.query(Program).filter(Program.code == p["code"]).first()
        if exists:
            continue

        program = Program(
            title=p["title"],
            description=p["description"],
            code=p["code"],
            semester=p["semester"],
            is_active=True,
        )
        db.add(program)

    db.commit()
    db.close()
    print("✅ Programs seeded")
