from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta
from typing import List

from app.dependencies import get_db, get_current_user
from app.models.subscription import Subscription, UserSubscription
from app.schemas.subscription import SubscriptionOut, SubscribeCoursesIn, MultipleSubscribeIn

router = APIRouter(prefix="/subscribe",tags=["Subscriptions"])


# ------------------ UTILITAIRE ------------------
def create_user_subscription(user_id: int, sub: Subscription) -> UserSubscription:
    start = date.today()
    end = start + timedelta(days=sub.duration_days)
    return UserSubscription(
        user_id=user_id,
        subscription_id=sub.id,
        start_date=start,
        end_date=end,
        is_active=True
    )


def is_active(db: Session, user_id: int, subscription_id: int) -> bool:
    return db.query(UserSubscription).filter_by(
        user_id=user_id, subscription_id=subscription_id, is_active=True
    ).first() is not None


# =================== LISTER LES ABONNEMENTS ===================
@router.get("/", response_model=List[SubscriptionOut])
def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()


# =================== S'ABONNER À MULTIPLES ===================
@router.post("/multiple", response_model=List[SubscriptionOut])
def subscribe_multiple(payload: MultipleSubscribeIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    subscription_ids = list(set(payload.subscription_ids))
    subscriptions_to_add = []

    for sub_id in subscription_ids:
        sub = db.get(Subscription, sub_id)
        if not sub or is_active(db, user.id, sub_id):
            continue
        subscriptions_to_add.append(create_user_subscription(user.id, sub))

    if not subscriptions_to_add:
        raise HTTPException(status_code=400, detail="No new subscriptions to add")

    db.add_all(subscriptions_to_add)
    db.commit()
    return subscriptions_to_add


# =================== S'ABONNER À UN SEUL ===================
@router.post("/{subscription_id}", response_model=SubscriptionOut)
def subscribe_single(subscription_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sub = db.get(Subscription, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if is_active(db, user.id, subscription_id):
        raise HTTPException(status_code=400, detail="Already subscribed")

    user_sub = create_user_subscription(user.id, sub)
    db.add(user_sub)
    db.commit()
    db.refresh(user_sub)
    return user_sub



@router.post("", response_model=List[str])
def subscribe_to_courses(payload: SubscribeCoursesIn, db: Session = Depends(get_db), user=Depends(get_current_user)):

    print("Payload:", payload.course_ids, payload.billing)
    created = []

    for course_id in payload.course_ids:

        print("Checking course_id:", course_id)

        sub = db.query(Subscription).filter(
            Subscription.course_id == course_id,
            Subscription.billing_type == payload.billing
        ).first()

        print("Subscription found:", sub)

        if not sub:
            print("❌ No subscription matched")
            continue

        active = is_active(db, user.id, sub.id)
        print("Already active:", active)

        if active:
            print("❌ User already subscribed")
            continue

        user_sub = create_user_subscription(user.id, sub)
        db.add(user_sub)
        created.append(sub.name)
    all_subs = db.query(Subscription).all()
    print("ALL SUBSCRIPTIONS:")
    for s in all_subs:
        print(s.id, s.course_id, s.name)

    print("Created:", created)

    if not created:
        raise HTTPException(status_code=400, detail="No new subscriptions added")

    db.commit()
    return created

# =================== RÉCUPÉRER LES COURS DE L'UTILISATEUR ===================
@router.get("/my-courses")
def my_courses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_subs = (
        db.query(UserSubscription)
        .options(joinedload(UserSubscription.subscription).joinedload(Subscription.course))
        .filter(
            UserSubscription.user_id == user.id,
            UserSubscription.is_active == True
        )
        .all()
    )

    courses = [
        {
            "id": us.subscription.course.id,
            "title": us.subscription.course.title,
            "description": us.subscription.course.description,
            "created_at": us.subscription.course.created_at
        }
        for us in user_subs
        if us.subscription and us.subscription.course
    ]
    return courses