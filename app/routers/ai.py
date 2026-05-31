from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.openai_client import ask_ai
from app.ai.prompt import AI_TUTOR_PROMPT
from openai import RateLimitError

router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):

    messages = [
        {"role": "system", "content": AI_TUTOR_PROMPT},
        {"role": "user", "content": req.message}
    ]

    try:
        reply = ask_ai(messages)

    except RateLimitError:

        reply = "Quota OpenAI dépassé. Merci de vérifier votre compte."


    return {"reply": reply}