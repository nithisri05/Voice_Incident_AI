import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def generate_confirmation_speech(structured):

    text = "Incident recorded."

    if structured.get("equipment"):
        text += f" {structured['equipment']}"

    if structured.get("location_or_unit"):
        text += f" in {structured['location_or_unit']}"

    if structured.get("incident_time"):
        text += f" at {structured['incident_time']}."

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    audio_bytes = response.read()

    return audio_bytes, text