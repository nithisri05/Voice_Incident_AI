import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def transcribe_audio(audio_stream):
    """
    Fast Whisper transcription.
    Uses direct memory stream.
    """

    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_stream,
        temperature=0
    )

    return response.text.strip()