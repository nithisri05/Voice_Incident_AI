from flask import Flask, render_template, request, jsonify, send_from_directory
from audio_handler import save_audio_file
from audio_converter import convert_webm_to_wav
from stt_service import transcribe_audio
from semantic_service import extract_structured_data
from tts_service import generate_confirmation_speech
from report_storage import save_report_to_excel
from datetime import datetime
import os
import uuid

app = Flask(__name__)

TTS_FOLDER = os.path.join("static", "tts_audio")
os.makedirs(TTS_FOLDER, exist_ok=True)


def auto_fill_datetime(structured):
    now = datetime.now()

    if not structured.get("incident_date"):
        structured["incident_date"] = now.strftime("%Y-%m-%d")

    if not structured.get("incident_time"):
        structured["incident_time"] = now.strftime("%H:%M")

    return structured


def is_valid(structured):

    if not structured.get("equipment"):
        return False

    if not structured.get("incident_summary"):
        return False

    if not structured.get("location_or_unit"):
        return False

    return True


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_audio", methods=["POST"])
def upload_audio():

    if "audio" not in request.files:
        return jsonify({"error": "No audio received"}), 400

    audio_file = request.files["audio"]

    webm_path = save_audio_file(audio_file)
    wav_path = convert_webm_to_wav(webm_path)

    transcript = transcribe_audio(wav_path)

    structured = extract_structured_data(transcript)

    structured = auto_fill_datetime(structured)

    print("FINAL STRUCTURED:", structured)

    if not is_valid(structured):
        return jsonify({
            "transcript": transcript,
            "structured": structured,
            "needs_clarification": True,
            "clarification_question": "Please specify equipment, location, and what happened."
        })

    # Save immediately (fast demo)
    save_report_to_excel(structured)

    audio_bytes, confirmation_text = generate_confirmation_speech(structured)

    filename = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join(TTS_FOLDER, filename)

    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    return jsonify({
        "transcript": transcript,
        "structured": structured,
        "needs_clarification": False,
        "confirmation_text": confirmation_text,
        "tts_audio_url": f"/tts_audio/{filename}"
    })


@app.route("/tts_audio/<filename>")
def serve_tts(filename):
    return send_from_directory(TTS_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=False)