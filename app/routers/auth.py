from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    UploadFile,
    Form,
    File,
    Request
)

from sqlalchemy.orm import Session
import shutil
import os
from uuid import uuid4
import secrets

from google.oauth2 import id_token
from google.auth.transport import requests

from app.models.user import User
from app.schemas.user import (
    RegisterSchema,
    LoginSchema,
    VerifyOTPSchema,
    UserOut,
    ChangePasswordSchema
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

from app.dependencies import get_db, get_current_user
from app.utils.send_email import (
    welcome_email,
    otp_email,
    send_email
)

router = APIRouter(tags=["Auth"])

FAKE_OTP = "123456"
GOOGLE_CLIENT_ID = "974675121498-ic32r1j1ooto7eq0bnohkh8dk4vfrsgo.apps.googleusercontent.com"

UPLOAD_DIR = "uploads/users"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ================= REGISTER =================
@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already exists")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()

    send_email(
        to_email=data.email,
        subject="Welcome to H-Learning!",
        html_content=welcome_email(data.name)
    )

    send_email(
        to_email=data.email,
        subject="Your OTP Code",
        html_content=otp_email(FAKE_OTP)
    )

    return {"message": "OTP sent. Welcome email delivered!"}


# ================= VERIFY OTP =================
@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPSchema,
    response: Response,
    db: Session = Depends(get_db)
):

    if data.otp != FAKE_OTP:
        raise HTTPException(400, "Invalid OTP")

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(404, "User not found")

    token = create_access_token(
        {"user_id": user.id},
        data.remember_me
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return {"message": "Authenticated"}


# ================= LOGIN =================
@router.post("/login")
def login(
    data: LoginSchema,
    response: Response,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=404, detail="Wrong Email or password")

    token = create_access_token(
        {"user_id": user.id},
        data.remember_me
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return {
        "message": "Logged in",
        "role": user.role,
        "user_id": user.id
    }


# ================= LOGOUT =================
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


# ================= ME =================
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


# ================= CHANGE PASSWORD =================
@router.post("/change-password")
def change_password(
    data: ChangePasswordSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    user.old_password_hash = user.password_hash
    user.password_hash = hash_password(data.new_password)

    db.add(user)
    db.commit()

    return {"message": "Password changed successfully"}


# ================= UPDATE PROFILE =================
@router.put("/update-profile")
def update_profile(
    name: str = Form(...),
    email: str = Form(...),
    university: str = Form(None),
    program: str = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    existing_user = db.query(User).filter(
        User.email == email,
        User.id != user.id
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user.name = name
    user.email = email.lower()

    if university:
        user.onboarding = user.onboarding or {}
        user.onboarding["university"] = university

    if program:
        user.onboarding = user.onboarding or {}
        user.onboarding["program"] = program

    if photo:
        filename = f"{uuid4().hex}_{photo.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        user.photo_url = f"/{UPLOAD_DIR}/{filename}"

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "name": user.name,
            "email": user.email,
            "photo_url": user.photo_url,
            "university": university,
            "program": program
        }
    }


# ================= GOOGLE LOGIN =================
@router.post("/google")
def google_login(data: dict, response: Response, db: Session = Depends(get_db)):

    try:
        idinfo = id_token.verify_oauth2_token(
            data["token"],
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(400, "Invalid Google token")

    email = idinfo["email"]
    name = idinfo.get("name")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(secrets.token_hex(16))
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"user_id": user.id}, False)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return {"message": "Google login success"}