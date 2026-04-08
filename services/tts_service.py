import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def generate_confirmation_speech(data):

    text = "Incident report recorded successfully."

    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
            timeout=5  # 🔥 prevent long waiting
        )

        audio_bytes = response.read()
        return audio_bytes, text

    except Exception as e:
        print("TTS ERROR:", e)

        # 🔥 fallback (no crash)
        return None, text