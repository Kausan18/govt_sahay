import os
from groq import Groq

# Lazy load — client created on first use, not at import time
# This prevents startup crash if GROQ_API_KEY is missing
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in your .env file")
        _client = Groq(api_key=api_key)
    return _client


def ask_about_scheme(scheme: dict, user_question: str, language: str = "English") -> str:
    system_prompt = f"""You are a helpful government scheme advisor for India.
Answer questions about this scheme in {language}.
Scheme details: {scheme}
Keep answers simple, clear, and under 150 words. Use bullet points where helpful."""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content


def situational_query(profile: dict, user_situation: str, all_schemes: list) -> str:
    scheme_names = [s["name"] for s in all_schemes[:20]]
    system_prompt = f"""You are a government scheme advisor for India.
User profile: {profile}
Available schemes: {scheme_names}
Help the user find the most relevant scheme for their situation.
Be conversational and empathetic. Suggest 2-3 schemes max."""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_situation}
        ],
        max_tokens=400
    )
    return response.choices[0].message.content