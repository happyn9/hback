import hashlib
import hmac
import logging
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from datetime import date, timedelta

from app.core.config import settings
from app.dependencies import get_db, get_current_user
from app.models.subscription import Subscription, UserSubscription

router = APIRouter(prefix="/pay", tags=["Payment"])
logger = logging.getLogger("payments")

FLW_SECRET_KEY  = settings.FLUTTERWAVE_SECRET_KEY
FLW_WEBHOOK_HASH = settings.FLUTTERWAVE_WEBHOOK_HASH
FRONTEND_URL=settings.FRONTEND_URL
BACKEND_URL     = settings.BACKEND_URL

PHONE_REGEX = re.compile(r"^\d{9,10}$")

OPERATOR_MAP = {
    "mtn":    "MTN",
    "airtel": "AIRTEL",
    "zam":    "ZAMTEL",
}


# ─────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────
class InitiatePaymentIn(BaseModel):
    course_id: int
    billing:   str    # "monthly" | "yearly"
    phone:     str    # ex: "0971234567"
    operator:  str    # "mtn" | "airtel" | "zam"

    @field_validator("operator")
    @classmethod
    def operator_must_be_known(cls, v: str) -> str:
        if v not in OPERATOR_MAP:
            raise ValueError(f"Invalid operator '{v}'. Expected one of {list(OPERATOR_MAP)}")
        return v

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v: str) -> str:
        cleaned = v.replace(" ", "")
        if not PHONE_REGEX.match(cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned

    @field_validator("billing")
    @classmethod
    def billing_must_be_known(cls, v: str) -> str:
        if v not in ("monthly", "yearly"):
            raise ValueError("billing must be 'monthly' or 'yearly'")
        return v


# ─────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────
def create_user_subscription(user_id: int, sub: Subscription) -> UserSubscription:
    start = date.today()
    end   = start + timedelta(days=sub.duration_days)
    return UserSubscription(
        user_id=user_id,
        subscription_id=sub.id,
        start_date=start,
        end_date=end,
        is_active=True
    )


def is_active(db: Session, user_id: int, subscription_id: int) -> bool:
    return db.query(UserSubscription).filter_by(
        user_id=user_id,
        subscription_id=subscription_id,
        is_active=True
    ).first() is not None


def activate_subscription_if_valid(
    db: Session,
    tx_ref: str,
    transaction: dict,
) -> tuple[bool, str, Subscription | None]:
    """
    Logique centrale, réutilisée par /callback ET /webhook :
    parse le tx_ref, vérifie le montant/devise, et active l'abonnement.
    Retourne (ok, reason, subscription).
    """
    try:
        parts   = tx_ref.split("-")  # ["HLEARN", "3", "7", "20240623"]
        user_id = int(parts[1])
        sub_id  = int(parts[2])
    except (IndexError, ValueError):
        logger.warning("tx_ref invalide reçu: %s", tx_ref)
        return False, "invalid_ref", None

    sub = db.get(Subscription, sub_id)
    if not sub:
        return False, "subscription_not_found", None

    # Vérification du montant et de la devise — CRITIQUE pour éviter la fraude
    paid_amount   = float(transaction.get("amount", 0) or 0)
    paid_currency = transaction.get("currency")

    if paid_currency != "ZMW":
        logger.error("Devise inattendue pour tx_ref=%s: %s", tx_ref, paid_currency)
        return False, "currency_mismatch", sub

    if paid_amount < float(sub.price):
        logger.error(
            "Montant insuffisant pour tx_ref=%s: payé=%s attendu=%s",
            tx_ref, paid_amount, sub.price
        )
        return False, "amount_mismatch", sub

    if is_active(db, user_id, sub_id):
        logger.info("User %s déjà abonné à sub %s (idempotence)", user_id, sub_id)
        return True, "already_active", sub

    user_sub = create_user_subscription(user_id, sub)
    db.add(user_sub)
    db.commit()
    logger.info("UserSubscription créée: user=%s sub=%s cours=%s", user_id, sub_id, sub.course_id)
    return True, "activated", sub


async def verify_transaction_with_flutterwave(transaction_id: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            verif = await client.get(
                f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
                headers={"Authorization": f"Bearer {FLW_SECRET_KEY}"}
            )
        verif.raise_for_status()
        return verif.json()
    except httpx.HTTPError as exc:
        logger.error("Erreur lors de la vérification Flutterwave: %s", exc)
        raise HTTPException(status_code=502, detail="Payment verification service unavailable")


# ─────────────────────────────────────────────
# ÉTAPE 1 — Initier le paiement
# POST /pay/initiate
# ─────────────────────────────────────────────
@router.post("/initiate")
async def initiate_payment(
    payload: InitiatePaymentIn,
    db:      Session = Depends(get_db),
    user                = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.course_id    == payload.course_id,
        Subscription.billing_type == payload.billing
    ).first()

    if not sub:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    if is_active(db, user.id, sub.id):
        raise HTTPException(status_code=400, detail="Already subscribed to this course")

    # Référence unique : HLEARN-{user_id}-{sub_id}-{date}
    tx_ref = f"HLEARN-{user.id}-{sub.id}-{date.today().strftime('%Y%m%d%H%M%S')}"

    flw_network = OPERATOR_MAP[payload.operator]  # déjà validé par le schema

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.flutterwave.com/v3/payments",
                headers={
                    "Authorization": f"Bearer {FLW_SECRET_KEY}",
                    "Content-Type":  "application/json",
                },
                json={
                    "tx_ref":          tx_ref,
                    "amount":          sub.price,
                    "currency":        "ZMW",
                    "payment_options": "mobilemoney",
                    "redirect_url":    f"{BACKEND_URL}/pay/callback",
                    "customer": {
                        "email":       user.email,
                        "name":        user.name,
                        "phonenumber": payload.phone,
                    },
                    "meta": {
                        "mobile_money_operator": flw_network,
                        "mobile_number":         payload.phone,
                        "country":               "ZM",
                    },
                    "customizations": {
                        "title":       "H-Learning",
                        "description": f"Accès : {sub.name}",
                    },
                }
            )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Erreur appel Flutterwave /payments: %s", exc)
        raise HTTPException(status_code=502, detail="Payment provider unavailable, try again later")

    data = response.json()

    if data.get("status") != "success":
        logger.error("Flutterwave a rejeté la requête: %s", data)
        raise HTTPException(
            status_code=502,
            detail=data.get("message", "Flutterwave rejected the request")
        )

    return {
        "payment_url": data["data"]["link"],
        "tx_ref":      tx_ref,
        "amount":      sub.price,
        "plan":        sub.name,
    }


# ─────────────────────────────────────────────
# ÉTAPE 2 — Callback après paiement (redirect navigateur)
# GET /pay/callback  ← Flutterwave redirige ici
#
# IMPORTANT : ce n'est qu'un confort UX. La vraie source de
# vérité reste le webhook ci-dessous, car l'utilisateur peut
# fermer son navigateur avant d'être redirigé ici alors que
# le paiement mobile money a bien été validé côté opérateur.
# ─────────────────────────────────────────────
@router.get("/callback")
async def payment_callback(
    status:         str,
    tx_ref:         str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    logger.info("Callback reçu: status=%s tx_ref=%s transaction_id=%s", status, tx_ref, transaction_id)

    if status != "successful":
        return RedirectResponse(
            f"{FRONTEND_URL}/payment/failed?ref={tx_ref}&status={status}"
        )

    verif_data  = await verify_transaction_with_flutterwave(transaction_id)
    transaction = verif_data.get("data", {})

    if (
        verif_data.get("status") != "success"
        or transaction.get("tx_ref") != tx_ref
        or transaction.get("status") != "successful"
    ):
        return RedirectResponse(
            f"{FRONTEND_URL}/payment/failed?ref={tx_ref}&reason=verification_failed"
        )

    ok, reason, sub = activate_subscription_if_valid(db, tx_ref, transaction)

    if not ok:
        return RedirectResponse(
            f"{FRONTEND_URL}/payment/failed?ref={tx_ref}&reason={reason}"
        )

    if reason == "already_active":
        return RedirectResponse(
            f"{FRONTEND_URL}/course-info/{sub.course_id}?already_subscribed=true"
        )

    return RedirectResponse(
        f"{FRONTEND_URL}/course-info/{sub.course_id}?payment=success"
    )


# ─────────────────────────────────────────────
# ÉTAPE 2bis — Webhook serveur-à-serveur (source de vérité)
# POST /pay/webhook  ← configuré dans le dashboard Flutterwave
# ─────────────────────────────────────────────
@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    # 1. Authentifier l'appel : Flutterwave envoie le secret hash configuré
    #    dans le header 'verif-hash'. Comparaison en temps constant.
    received_hash = request.headers.get("verif-hash", "")
    if not FLW_WEBHOOK_HASH or not hmac.compare_digest(received_hash, FLW_WEBHOOK_HASH):
        logger.warning("Webhook rejeté: hash invalide ou manquant")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    body = await request.json()
    logger.info("Webhook reçu: event=%s", body.get("event"))

    if body.get("event") != "charge.completed":
        # On ignore les autres types d'événements
        return {"status": "ignored"}

    data = body.get("data", {})
    if data.get("status") != "successful":
        return {"status": "ignored_not_successful"}

    transaction_id = data.get("id")
    tx_ref          = data.get("tx_ref")

    if not transaction_id or not tx_ref:
        logger.warning("Webhook avec données incomplètes: %s", data)
        return {"status": "ignored_incomplete"}

    # 2. Re-vérifier auprès de Flutterwave (ne jamais faire confiance
    #    uniquement au payload du webhook, qui pourrait être rejoué)
    verif_data  = await verify_transaction_with_flutterwave(transaction_id)
    transaction = verif_data.get("data", {})

    if (
        verif_data.get("status") != "success"
        or transaction.get("tx_ref") != tx_ref
        or transaction.get("status") != "successful"
    ):
        logger.warning("Webhook: vérification Flutterwave échouée pour tx_ref=%s", tx_ref)
        return {"status": "verification_failed"}

    ok, reason, sub = activate_subscription_if_valid(db, tx_ref, transaction)
    return {"status": reason if ok else f"failed:{reason}"}


# ─────────────────────────────────────────────
# BONUS — Vérifier si un cours est déjà payé
# GET /pay/check/{course_id}
# ─────────────────────────────────────────────
@router.get("/check/{course_id}")
def check_subscription(
    course_id: int,
    db:        Session = Depends(get_db),
    user                = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.course_id == course_id
    ).first()

    if not sub:
        return {"subscribed": False}

    return {"subscribed": is_active(db, user.id, sub.id)}