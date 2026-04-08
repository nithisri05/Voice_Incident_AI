import os
from openai import OpenAI
from dotenv import load_dotenv

# ---------------- LOAD ENV PROPERLY ----------------

# Get project root (Voice_Incident_AI/Voice_Incident_AI)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Force load .env from root
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# ---------------- GET CONFIG ----------------

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

# ---------------- DEBUG (REMOVE LATER) ----------------
print("STT SERVICE INIT")
print("ENV PATH:", ENV_PATH)
print("API KEY LOADED:", "YES" if API_KEY else "NO")

# ---------------- VALIDATION ----------------

if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file location.")

# ---------------- CREATE CLIENT ----------------

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL  # supports your custom base URL
)

# ---------------- MAIN FUNCTION ----------------

def transcribe_audio(audio_stream):
    """
    Fast Whisper transcription using in-memory audio stream.
    """

    try:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream,
            temperature=0
        )

        return response.text.strip()

    except Exception as e:
        print("STT Error:", str(e))
        return "Error in transcription"