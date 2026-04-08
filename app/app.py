import os
import sys
import uuid
import threading
import pandas as pd

from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# GOOGLE AUTH
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.audio_handler import save_audio_file
from services.stt_service import transcribe_audio
from services.semantic_service import extract_structured_data
from services.tts_service import generate_confirmation_speech
from report_storage import save_report_to_excel

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "incident_voice_key"

# ================= GOOGLE CONFIG =================

GOOGLE_CLIENT_ID = "284391924030-6364to5tehb446ru4fm446e7abk9ag4g.apps.googleusercontent.com"

# ================= STRICT AUTH =================

ADMIN_EMAIL = "nithisri.bm23@bitsathy.ac.in"
USER_EMAIL = "nithisri.arunkumar@gmail.com"


def detect_role(email):
    email = email.lower().strip()

    if email == ADMIN_EMAIL:
        return "admin"

    if email == USER_EMAIL:
        return "user"

    return None


def require_role(role):
    return session.get("role") == role


# ================= GOOGLE LOGIN =================

@app.route("/google_login", methods=["POST"])
def google_login():

    token = request.json.get("credential")

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            grequests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email", "").lower()

        role = detect_role(email)

        if not role:
            return jsonify({
                "error": "❌ Access denied. Use authorized email only."
            }), 403

        session["email"] = email
        session["role"] = role

        if role == "admin":
            return jsonify({"redirect": "/dashboard"})
        else:
            return jsonify({"redirect": "/"})

    except Exception:
        return jsonify({"error": "Invalid Google login"}), 400


# ================= ROUTES =================

@app.route("/")
def home():
    if not require_role("user"):
        return redirect("/login")
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if not require_role("admin"):
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/api/incidents")
def incidents():

    if not require_role("admin"):
        return jsonify([])

    file = os.path.join(BASE_DIR, "app", "incident_reports.xlsx")

    if not os.path.exists(file):
        return jsonify([])

    df = pd.read_excel(file).fillna("")
    return jsonify(df.to_dict(orient="records"))


# ================= MEMORY =================

CORE_FIELDS = [
    "equipment",
    "location_or_unit",
    "department",
    "incident_summary"
]


def reset_conversation():
    session["conversation_text"] = ""
    session["conversation_data"] = {}
    session["question_asked"] = False


def init_session():
    if "conversation_text" not in session:
        reset_conversation()


# ================= HELPERS =================

def merge_data(old, new):
    for k, v in new.items():
        if v:
            old[k] = v
    return old


def get_missing_core(data):
    return [f for f in CORE_FIELDS if not data.get(f)]


def generate_followup(field):
    mapping = {
        "equipment": "Which equipment is involved?",
        "location_or_unit": "Which unit or location?",
        "department": "Which department?",
        "incident_summary": "What exactly happened?"
    }
    return mapping.get(field, f"Please specify {field}")


# ================= MAIN =================

@app.route("/upload_audio", methods=["POST"])
def upload_audio():

    if not require_role("user"):
        return jsonify({"error": "Unauthorized"}), 403

    init_session()

    transcript = ""

    # TEXT INPUT
    if "text" in request.form and request.form["text"].strip():
        transcript = request.form["text"].lower().strip()

    # AUDIO INPUT
    elif "audio" in request.files:
        audio_file = request.files["audio"]

        if audio_file.filename != "":
            audio_stream = save_audio_file(audio_file)
            transcript = transcribe_audio(audio_stream).lower().strip()

    if not transcript:
        return jsonify({"error": "No valid input"}), 400

    session["conversation_text"] += " " + transcript
    full_text = session["conversation_text"]

    new_data = extract_structured_data(transcript, full_text)

    session["conversation_data"] = merge_data(
        session["conversation_data"], new_data
    )

    final_data = session["conversation_data"]

    missing = get_missing_core(final_data)

    if missing and not session.get("question_asked"):
        question = generate_followup(missing[0])
        session["question_asked"] = True

        return jsonify({
            "transcript": full_text,
            "structured": final_data,
            "needs_clarification": True,
            "clarification_question": question
        })

    # SAVE
    threading.Thread(
        target=save_report_to_excel,
        args=(final_data,),
        daemon=True
    ).start()

    # TTS
    audio_bytes, _ = generate_confirmation_speech(final_data)

    tts_url = None
    if audio_bytes:
        filename = f"{uuid.uuid4()}.mp3"
        path = os.path.join(STATIC_DIR, "tts_audio", filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            f.write(audio_bytes)

        tts_url = f"/tts_audio/{filename}"

    result = {
        "transcript": full_text,
        "structured": final_data,
        "needs_clarification": False,
        "tts_audio_url": tts_url
    }

    reset_conversation()
    return jsonify(result)


# ================= RUN =================

if __name__ == "__main__":
    print("🚀 Running with Google Login (STRICT MODE)")
    app.run(debug=True)