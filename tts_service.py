import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def generate_confirmation_speech(structured):

    text = (
        f"Incident recorded in {structured.get('location_or_unit')} "
        f"on {structured.get('incident_date')} "
        f"at {structured.get('incident_time')}. "
        f"The {structured.get('equipment')} "
        f"{structured.get('incident_summary')}. "
    )

    if structured.get("severity"):
        text += f"Severity level is {structured.get('severity')}."

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    audio_bytes = response.read()

    return audio_bytes, text