from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
from pydantic import BaseModel
from datetime import date, timedelta

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

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# =================== APP ===================
app = FastAPI(title="H-Learning API 🚀")


# =================== MIDDLEWARE ===================
class COOPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        return response


app.add_middleware(COOPMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://h-learning-wine.vercel.app",
        "https://hback-3.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================== ROUTERS ===================
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


# =================== STATIC FILES ===================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# =================== STARTUP ===================
@app.on_event("startup")
def startup():
    print("🚀 App started - DB managed by Alembic")


# =================== SCHEMAS (OK TEMPORAIRE) ===================
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


# =================== FAKE DATA ===================
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


@app.get("/")
def read_root():
    return {"message": "Welcome to H-Learning API 🚀"}



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
