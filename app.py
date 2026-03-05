from flask import Flask, render_template, request, jsonify, send_from_directory, session
from audio_handler import save_audio_file
from stt_service import transcribe_audio
from semantic_service import extract_structured_data
from tts_service import generate_confirmation_speech
from report_storage import save_report_to_excel
from datetime import datetime
import os
import uuid
import time
import threading

app = Flask(__name__)
app.secret_key = "incident_voice_key"

TTS_FOLDER = os.path.join("static", "tts_audio")
os.makedirs(TTS_FOLDER, exist_ok=True)

MANDATORY_FIELDS = ["equipment", "location_or_unit", "incident_summary"]


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


def auto_fill_datetime(data):

    now = datetime.now()

    if not data.get("incident_date"):
        data["incident_date"] = now.strftime("%Y-%m-%d")

    if not data.get("incident_time"):
        data["incident_time"] = now.strftime("%H:%M")

    return data


def is_valid(data):

    for field in MANDATORY_FIELDS:
        if not data.get(field):
            return False

    return True


def clarification_question(data):

    if not data.get("equipment"):
        return "Which equipment was involved?"

    if not data.get("location_or_unit"):
        return "Which unit or location did this occur?"

    if not data.get("incident_summary"):
        return "What exactly happened?"

    return ""


@app.route("/")
def home():

    if "conversation_text" not in session:
        reset_conversation()

    return render_template("index.html")


@app.route("/upload_audio", methods=["POST"])
def upload_audio():

    start = time.time()

    if "audio" not in request.files:
        return jsonify({"error": "No audio"}), 400

    audio_file = request.files["audio"]

    webm_path = save_audio_file(audio_file)

    transcript = transcribe_audio(webm_path)

    transcript = transcript.lower().strip()

    if "conversation_text" not in session:
        reset_conversation()

    # append transcript to conversation memory
    session["conversation_text"] += " " + transcript

    full_text = session["conversation_text"]

    # extract structured data from full conversation
    new_data = extract_structured_data(full_text)

    conversation = session["conversation_data"]

    for key, value in new_data.items():
        if value and not conversation.get(key):
            conversation[key] = value

    conversation = auto_fill_datetime(conversation)

    session["conversation_data"] = conversation

    if not is_valid(conversation):

        question = clarification_question(conversation)

        return jsonify({
            "transcript": full_text,
            "structured": conversation,
            "needs_clarification": True,
            "clarification_question": question
        })

    # Save report
    threading.Thread(
      target=save_report_to_excel,
      args=(conversation,),
      daemon=True
    ).start()

    audio_bytes, confirmation_text = generate_confirmation_speech(conversation)

    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join(TTS_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(audio_bytes)

    total = round(time.time() - start, 2)

    print("Processing time:", total)

    result = {
        "transcript": full_text,
        "structured": conversation,
        "needs_clarification": False,
        "confirmation_text": confirmation_text,
        "tts_audio_url": f"/tts_audio/{filename}",
        "processing_time": total
    }

    # reset conversation AFTER saving
    reset_conversation()

    return jsonify(result)


@app.route("/tts_audio/<filename>")
def serve_tts(filename):
    return send_from_directory(TTS_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=False)