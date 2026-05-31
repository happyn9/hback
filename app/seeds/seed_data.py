from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool
from app.core.database import SessionLocal
from app.models.program import Program
from app.models.subscription import Subscription
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.lesson import Lesson



# =========================
# COURSES
# =========================
COURSES_DATA = [
    {
        "title": "Python for Beginners",
        "description": "Learn Python from scratch, including basics, OOP, and projects.",
        "program_code": "se",
        "is_premium": True,
        "order_index": 1,
        "image_url": "https://programming.dev/pictrs/image/644d1bd4-dfc1-4a39-b667-6d7c8f353b5b.jpeg?format=webp",
        "daily_price": 5.0,
        "weekly_price": 20.0,
        "monthly_price": 60.0,
        "tags": ["python", "beginner", "programming"],
        "course_requirements": [
            "No prior programming knowledge required",
            "Basic computer skills",
        ],
        "what_you_will_learn": [
            "Learn Python 3",
            "Master core concepts: types, lists, functions",
            "Understand Object-Oriented Programming",
            "Work with virtual environments",
            "Use modern Python syntax",
            "Explore built-in Python features",
            "Use the standard library & PyPI",
            "Write unit tests",
        ],
        "videos": [
            "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "https://www.youtube.com/watch?v=HGOBQPFzWKo",
            "https://www.youtube.com/watch?v=8ext9G7xspg",
        ],
        "pdf": "https://example.com/pdfs/python_course.pdf",
    },
    {
        "title": "React JS Advanced",
        "description": "Build complex React applications using hooks, context, and Redux.",
        "program_code": "se",
        "is_premium": True,
        "order_index": 2,
        "image_url": "https://www.mbloging.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fyynr1uml%2Fproduction%2Fd3f0ff2ab5398aaffb00fa0b3afcb238772f42e7-1024x576.jpg%3Fw%3D1024%26auto%3Dformat&w=3840&q=75",
        "daily_price": 7.0,
        "weekly_price": 30.0,
        "monthly_price": 80.0,
        "tags": ["react", "javascript", "frontend"],
        "course_requirements": [
            "Basic knowledge of JavaScript and HTML/CSS",
            "Familiarity with React basics recommended",
        ],
        "what_you_will_learn": [
            "Build complex React applications",
            "Use React hooks effectively",
            "Manage state with Context API and Redux",
            "Create reusable components",
            "Work with forms and validation",
            "Consume APIs and handle asynchronous calls",
            "Debug and test React applications",
            "Optimize React performance",
        ],
        "videos": [
            "https://www.youtube.com/watch?v=DLX62G4lc44",
            "https://www.youtube.com/watch?v=w7ejDZ8SWv8",
            "https://www.youtube.com/watch?v=9U3IhLAnSxM",
        ],
        "pdf": "https://example.com/pdfs/react_advanced.pdf",
    },
    {
        "title": "Web Development Bootcamp",
        "description": "HTML, CSS, JS, Node.js, Express, and MongoDB full stack course.",
        "program_code": "se",
        "is_premium": True,
        "order_index": 3,
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQEe1gnBJ0jT28VRO_htT814vg44eWReFV8_g&s",
        "daily_price": 8.0,
        "weekly_price": 35.0,
        "monthly_price": 90.0,
        "tags": ["web dev", "fullstack", "frontend", "backend"],
        "course_requirements": [
            "Basic understanding of computers",
            "No prior programming required",
        ],
        "what_you_will_learn": [
            "Build websites with HTML, CSS, and JavaScript",
            "Develop backend with Node.js and Express",
            "Work with databases using MongoDB",
            "Create RESTful APIs",
            "Deploy full stack applications",
            "Understand authentication & security basics",
            "Work with version control (Git)",
            "Build real-world projects",
        ],
        "videos": [
            "https://www.youtube.com/watch?v=Q33KBiDriJY",
            "https://www.youtube.com/watch?v=1NrHkjlWVhM",
            "https://www.youtube.com/watch?v=SBvmnHTQIPY",
        ],
        "pdf": "https://example.com/pdfs/web_dev_bootcamp.pdf",
    },
    {
        "title": "Object-Oriented Programming in Java",
        "description": "Learn OOP concepts, classes, inheritance, and interfaces in Java.",
        "program_code": "cs",
        "is_premium": True,
        "order_index": 4,
        "image_url": "https://raygun.com/blog/images/oop-concepts-java/feature.png",
        "daily_price": 6.0,
        "weekly_price": 25.0,
        "monthly_price": 70.0,
        "tags": ["java", "oop", "programming"],
        "course_requirements": [
            "Basic programming knowledge in any language",
            "Familiarity with Java syntax recommended",
        ],
        "what_you_will_learn": [
            "Understand OOP principles: encapsulation, inheritance, polymorphism",
            "Create and use classes and objects",
            "Implement interfaces and abstract classes",
            "Work with Java packages and libraries",
            "Handle exceptions properly",
            "Use Java collections",
            "Apply OOP concepts in projects",
            "Debug and test Java applications",
        ],
        "videos": [
            "https://www.youtube.com/watch?v=TBWX97e1E9g",
            "https://www.youtube.com/watch?v=H0Hw1j0h2AA",
            "https://www.youtube.com/watch?v=8cm1x4bC610",
        ],
        "pdf": "https://example.com/pdfs/java_oop.pdf",
    },
]


# =========================
# PROGRAMS
# =========================
PROGRAMS = [
    {"title": "Software Engineering", "description": "Programming, frontend, backend, and software architecture.", "code": "se", "semester": "All"},
    {"title": "Computer Science", "description": "Algorithms, data structures, and computer fundamentals.", "code": "cs", "semester": "All"},
    {"title": "English Tuition", "description": "Beginners, Intermediate, and Advanced.", "code": "eng", "semester": "All"},
    {"title": "Accounting & Finance", "description": "Finance, accounting, and business fundamentals.", "code": "af", "semester": "All"},
    {"title": "Networking", "description": "Networks, infrastructure, security, and systems.", "code": "net", "semester": "All"},
]

# =========================
# SEED FUNCTION
# =========================
def seed_database():
    db: Session = SessionLocal()
    try:
        # --- CREATE PROGRAMS ---
        for program_data in PROGRAMS:
            existing = db.query(Program).filter_by(code=program_data["code"]).first()
            if not existing:
                db.add(Program(**program_data))
        db.commit()

        # --- CREATE COURSES & CHAPTERS & LESSONS ---
        for course_data in COURSES_DATA:
            payload = course_data.copy()
            program_code = payload.pop("program_code")
            program = db.query(Program).filter_by(code=program_code).first()
            if not program:
                continue

            existing_course = db.query(Course).filter_by(title=course_data["title"]).first()
            if existing_course:
                continue

            videos = payload.pop("videos", [])
            pdf_url = payload.pop("pdf", None)

            course = Course(**payload, program_id=program.id)
            db.add(course)
            db.flush()

            video_index = 0
            # --- CREATE 5 CHAPTERS ---
            for chapter_number in range(1, 6):
                chapter = Chapter(
                    title=f"Chapter {chapter_number}",
                    order_index=chapter_number,
                    course_id=course.id
                )
                db.add(chapter)
                db.flush()

                if chapter_number < 5:
                    for lesson_number in range(1, 3):
                        youtube_url = videos[video_index % len(videos)] if videos else None
                        video_index += 1
                        lesson = Lesson(
                            title=f"Lesson {lesson_number}",
                            type="video",
                            youtube_url=youtube_url,
                            order_index=lesson_number,
                            chapter_id=chapter.id
                        )
                        db.add(lesson)
                else:
                    # Chapter 5 → final video + pdf + quiz
                    youtube_url = videos[video_index % len(videos)] if videos else None
                    final_video = Lesson(
                        title="Final Lesson",
                        type="video",
                        youtube_url=youtube_url,
                        order_index=1,
                        chapter_id=chapter.id
                    )
                    db.add(final_video)
                    if pdf_url:
                        pdf_lesson = Lesson(
                            title="Course Notes (PDF)",
                            type="pdf",
                            content_url=pdf_url,
                            order_index=2,
                            chapter_id=chapter.id
                        )
                        db.add(pdf_lesson)
                    quiz_lesson = Lesson(
                        title="Final Quiz",
                        type="quiz",
                        order_index=3,
                        chapter_id=chapter.id
                    )
                    db.add(quiz_lesson)

        db.commit()
        print("✅ Database seeded with 5 chapters per course!")
    except Exception as e:
        db.rollback()
        print("❌ Seeding error:", e)
    finally:
        db.close()

# =========================
# COURSE STATS (async version)
# =========================
async def course_stats_async(course_id: int) -> list[Lesson]:
    """
    Récupère toutes les leçons d'un cours donné, ordonnées par order_index.
    On fait un join avec Chapter car Lesson n'a pas directement course_id.
    """
    def get_lessons() -> list[Lesson]:
        db: Session = SessionLocal()
        try:
            lessons = (
                db.query(Lesson)
                .join(Chapter)
                .filter(Chapter.course_id == course_id)
                .order_by(Lesson.order_index)
                .all()
            )
            return lessons
        finally:
            db.close()

    lessons = await run_in_threadpool(get_lessons)
    return lessons