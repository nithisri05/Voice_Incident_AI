import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_from_directory, session
from datetime import datetime
import uuid
import time
import threading

from utils.audio_handler import save_audio_file
from services.stt_service import transcribe_audio
from services.semantic_service import extract_structured_data
from services.tts_service import generate_confirmation_speech
from report_storage import save_report_to_excel


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TTS_FOLDER = os.path.join(STATIC_DIR, "tts_audio")

os.makedirs(TTS_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

app.secret_key = "incident_voice_key"

MANDATORY_FIELDS = ["equipment", "location_or_unit", "incident_summary"]


# ---------------- RESET MEMORY ----------------

def reset_conversation():

    session["conversation_text"] = ""

    session["conversation_data"] = {
        "reporter_name": "",
        "department": "",
        "equipment": "",
        "incident_summary": "",
        "location_or_unit": "",
        "incident_date": "",
        "incident_time": "",
        "severity": "",
        "measured_parameters": "",
        "remarks": ""
    }


# ---------------- AUTO DATE TIME ----------------

def auto_fill_datetime(data):

    now = datetime.now()

    if not data.get("incident_date"):
        data["incident_date"] = now.strftime("%Y-%m-%d")

    if not data.get("incident_time"):
        data["incident_time"] = now.strftime("%H:%M")

    return data


# ---------------- VALIDATION ----------------

def is_valid(data):

    for field in MANDATORY_FIELDS:
        if not data.get(field):
            return False

    return True


# ---------------- CLARIFICATION ----------------

def clarification_question(data):

    if not data.get("equipment"):
        return "Which equipment was involved?"

    if not data.get("location_or_unit"):
        return "Which unit or location did this occur?"

    if not data.get("incident_summary"):
        return "What exactly happened?"

    return ""


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "conversation_text" not in session:
        reset_conversation()

    return render_template("index.html")


# ---------------- MAIN AUDIO API ----------------

@app.route("/upload_audio", methods=["POST"])
def upload_audio():

    start = time.time()

    if "audio" not in request.files:
        return jsonify({"error": "No audio"}), 400

    audio_file = request.files["audio"]

    audio_stream = save_audio_file(audio_file)

    transcript = transcribe_audio(audio_stream)

    transcript = transcript.lower().strip()

    if "conversation_text" not in session:
        reset_conversation()

    # store transcript history
    session["conversation_text"] += " " + transcript

    # IMPORTANT: extract only from current speech (fast)
    new_data = extract_structured_data(transcript)

    conversation = session["conversation_data"]

    # merge extracted data into memory
    for key, value in new_data.items():
        if value and not conversation.get(key):
            conversation[key] = value

    conversation = auto_fill_datetime(conversation)

    session["conversation_data"] = conversation

    # ask clarification if incomplete
    if not is_valid(conversation):

        question = clarification_question(conversation)

        return jsonify({
            "transcript": session["conversation_text"],
            "structured": conversation,
            "needs_clarification": True,
            "clarification_question": question
        })

    # save report asynchronously
    threading.Thread(
        target=save_report_to_excel,
        args=(conversation,),
        daemon=True
    ).start()

    # generate TTS
    audio_bytes, confirmation_text = generate_confirmation_speech(conversation)

    filename = f"{uuid.uuid4()}.mp3"

    file_path = os.path.join(TTS_FOLDER, filename)

    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    total_time = round(time.time() - start, 2)

    print("Processing time:", total_time)

    result = {
        "transcript": session["conversation_text"],
        "structured": conversation,
        "needs_clarification": False,
        "confirmation_text": confirmation_text,
        "tts_audio_url": f"/tts_audio/{filename}",
        "processing_time": total_time
    }

    # reset memory for next report
    reset_conversation()

    return jsonify(result)


# ---------------- SERVE TTS ----------------

@app.route("/tts_audio/<filename>")
def serve_tts(filename):

    return send_from_directory(TTS_FOLDER, filename)


# ---------------- WARMUP ----------------

def warmup():
    try:
        print("Warming up extraction model...")
        extract_structured_data("motor overheating at unit 5")
    except:
        pass

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

import pandas as pd

EXCEL_FILE = os.path.join(BASE_DIR, "app", "incident_reports.xlsx")

@app.route("/api/incidents")
def get_incidents():

    if not os.path.exists(EXCEL_FILE):
        return jsonify([])

    df = pd.read_excel(EXCEL_FILE)

    data = df.fillna("").to_dict(orient="records")

    return jsonify(data)


@app.route("/api/stats")
def get_stats():

    if not os.path.exists(EXCEL_FILE):
        return jsonify({"total": 0, "high": 0})

    df = pd.read_excel(EXCEL_FILE)

    total = len(df)

    high = 0
    if "severity" in df.columns:
        high = len(df[df["severity"].str.lower() == "high"])

    return jsonify({
        "total": total,
        "high": high
    })

if __name__ == "__main__":

    warmup()

    app.run(debug=False)