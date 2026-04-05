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


# In grok_service.py — replace ask_about_scheme
def ask_about_scheme(scheme: dict, user_question: str, language: str = "English") -> str:
    system_prompt = f"""You are a helpful Indian government scheme advisor.
Answer ONLY in {language}. Be simple, clear, and empathetic.
Scheme name: {scheme.get('name')}
Description: {scheme.get('description')}
Benefits: {scheme.get('benefits')}
Age limit: {scheme.get('min_age','any')} to {scheme.get('max_age','any')} years
Income limit: Rs.{scheme.get('income_limit','no limit')} per year
Required documents: {', '.join(scheme.get('required_docs', []))}
Official portal: {scheme.get('official_url', 'Not available')}
Answer the user's question using only the above information. If the answer is unknown, say so honestly."""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        max_tokens=400
    )
    return response.choices[0].message.content


def situational_query(profile: dict, user_situation: str, all_schemes: list) -> str:
    # Send top 10 schemes with name + description + key eligibility, not just names
    scheme_summaries = []
    for s in all_schemes[:10]:
        scheme_summaries.append({
            "name": s.get("name"),
            "description": s.get("description", "")[:100],
            "benefits": s.get("benefits", "")[:80],
            "income_limit": s.get("income_limit"),
            "occupations": s.get("occupations", []),
        })

    system_prompt = f"""You are a compassionate Indian government scheme advisor.
User's profile: Age {profile.get('age')}, {profile.get('gender')}, {profile.get('occupation')}, 
income Rs.{profile.get('income')}, state {profile.get('state')}, caste {profile.get('caste')}.
Available schemes (ranked by match score):
{scheme_summaries}
The user has described their situation. Suggest 2-3 most relevant schemes by name, explain why 
each applies to their situation, and what benefit they'd get. Be warm, simple, and speak like 
you are helping a family member. Respond in the same language the user writes in."""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_situation}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content