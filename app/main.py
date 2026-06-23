from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
from pydantic import BaseModel
from datetime import date, timedelta

from app.core.database import Base, engine, SessionLocal
from app.seeds.seed_data import seed_database

from app.routers import (
    auth,
    programs,
    courses,
    lessons,
    subscriptions,
    dashboard,
    recommendations,
    premium,
    chapters,
    admin,
    ai,
    workspace,
    upload,
    payment       
)




# =================== APP ===================
app = FastAPI(title="h-learning API")

# =================== MIDDLEWARE ===================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://192.168.0.104:5173",
    "https://feel-landed-legroom.ngrok-free.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================== ROUTERS ================----
app.include_router(auth.router, prefix="/auth")
app.include_router(subscriptions.router)
app.include_router(premium.router)
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(recommendations.router, prefix="/recommendations")
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(admin.router)
app.include_router(chapters.router)
app.include_router(ai.router)
app.include_router(programs.router, prefix="/programs")
app.include_router(workspace.router)
app.include_router(upload.router)
app.include_router(payment.router)   


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# =================== STARTUP ===================
@app.on_event("startup")
def startup():
    db = SessionLocal()
    
    Base.metadata.create_all(bind=engine)
    print("Tables created ✅")

    # Décommenter si tu veux peupler les données initiales


    db.commit()
    db.close()

"""from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()
admin_user = User(
    name="happy9",
    email="happy@gmail.com",
    password_hash=hash_password("31052003Ne@"),
    role="admin"
)
db.add(admin_user)
db.commit()
db.close()"""

# =================== MODELS ===================
class Summary(BaseModel):
    completed_lessons: int
    progress_percent: float
    streak_days: int

class WeeklyAnalytics(BaseModel):
    date: str
    minutes: int

class Analytics(BaseModel):
    weekly: List[WeeklyAnalytics]
    monthly_minutes: int

# =================== DUMMY DATA ===================
fake_summary = Summary(
    completed_lessons=12,
    progress_percent=35.0,
    streak_days=4
)

today = date.today()
fake_weekly = [
    WeeklyAnalytics(date=str(today - timedelta(days=i)), minutes=(i + 1) * 10)
    for i in range(7)
]
fake_analytics = Analytics(
    weekly=fake_weekly[::-1],
    monthly_minutes=sum([w.minutes for w in fake_weekly])
)

# =================== ENDPOINTS ===================
@app.get("/summary", response_model=Summary)
async def get_summary():
    return fake_summary

@app.get("/analytics", response_model=Analytics)
async def get_analytics():
    return fake_analytics

# =================== ROOT ===================
@app.get("/")
def read_root():
    return {"message": "Welcome to the h-learning API!"}



from app.core.database import SessionLocal
from app.models import Subscription, Course

def seed_subscriptions(db=None):
    if db is None:
        db = SessionLocal()

    try:
        # Vérifie si des subscriptions existent déjà
        if db.query(Subscription).count() > 0:
            print("Subscriptions already exist, skipping seeding.")
            return

        # Récupère tous les cours
        courses = db.query(Course).all()
        if not courses:
            print("No courses found in the database. Seeding aborted.")
            return

        subscriptions_to_add = []

        for course in courses:
            print(f"Checking course_id: {course.id}")
            for plan in [("Monthly Plan", 30, 29.99, "monthly"), ("Yearly Plan", 365, 199.99, "yearly")]:
                # Cherche dans la DB si déjà existant
                exists = db.query(Subscription).filter(
                    Subscription.course_id == course.id,
                    Subscription.billing_type == plan[3]
                ).first()
                if exists:
                    print(f"Subscription already exists: {exists.name} ({exists.billing_type})")
                    continue

                new_sub = Subscription(
                    name=plan[0],
                    description=f"{plan[1]} days access",
                    duration_days=plan[1],
                    price=plan[2],
                    billing_type=plan[3],
                    course_id=course.id
                )
                subscriptions_to_add.append(new_sub)
                print(f"Adding subscription: {plan[0]} for course {course.id}")

        # Ajoute toutes les subscriptions à la DB
        db.add_all(subscriptions_to_add)
        db.commit()

        print(f"{len(subscriptions_to_add)} subscriptions seeded ✅")
    finally:
        db.close()


# Exécution
seed_subscriptions()

