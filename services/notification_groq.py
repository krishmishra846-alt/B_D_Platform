import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_reminder(name: str, hours_left: int, language: str) -> str:
    """Uses Groq LPU to generate a rapid, context-aware localized reminder."""
    lang_map = {"hi": "Hindi", "mr": "Marathi", "en": "English"}
    
    prompt = f"""
    Write a brief, polite, and motivating blood donation reminder for a donor named {name}.
    The event is in {hours_left} hours.
    Language MUST be: {lang_map.get(language, 'English')}.
    Keep it strictly under 3 sentences. Do not use Markdown formatting.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq Generation Error: {e}")
        return f"Reminder: Your blood donation slot is in {hours_left} hours. Thank you, {name}!"