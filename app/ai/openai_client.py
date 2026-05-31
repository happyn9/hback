from openai import OpenAI
from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

def ask_ai(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=200,
        messages=messages
    )

    return response.choices[0].message.content