import sys
import os
import time
import jiwer
import re
import wave

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stt_service import transcribe_audio
from services.semantic_service import extract_structured_data

# ---------------- PATH CONFIGURATION ----------------
# Fixes FileNotFoundError by using absolute paths relative to this file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(SCRIPT_DIR, "test_audio")
GROUND_TRUTH_FILE = os.path.join(SCRIPT_DIR, "ground_truth.txt")


# ---------------- NUMBER NORMALIZATION ----------------

number_map = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
}

def normalize(text):
    if not text: return ""
    text = text.lower()
    for word, num in number_map.items():
        text = re.sub(rf"\b{word}\b", num, text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


# ---------------- UTILS ----------------

def get_audio_duration(file_path):
    with wave.open(file_path, "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        duration = frames / float(rate)
    return duration

def compute_rtf(process_time, audio_length):
    return process_time / audio_length if audio_length > 0 else 0


# ---------------- MAIN EVALUATION ----------------

def main():
    # Check if files exist before proceeding
    if not os.path.exists(GROUND_TRUTH_FILE):
        print(f"ERROR: Ground truth file not found at {GROUND_TRUTH_FILE}")
        return

    with open(GROUND_TRUTH_FILE, "r") as f:
        rows = [line.strip().split("|") for line in f.readlines() if line.strip()]

    if not os.path.exists(TEST_FOLDER):
        print(f"ERROR: Audio folder not found at {TEST_FOLDER}")
        return

    audio_files = sorted([f for f in os.listdir(TEST_FOLDER) if f.endswith(".wav")])

    total_wer = 0
    total_rtf = 0
    extraction_correct = 0

    print("\nEVALUATION TABLE\n")
    print(f"{'Test':<6}{'WER':<8}{'RTF':<8}{'Extraction':<12}")
    print("-" * 40)

    for i, audio_file in enumerate(audio_files):
        if i >= len(rows):
            print(f"Warning: No ground truth entry for {audio_file}. Skipping.")
            continue

        file_path = os.path.join(TEST_FOLDER, audio_file)

        # Reference data from ground_truth.txt
        reference = normalize(rows[i][0])
        expected_equipment = normalize(rows[i][1])
        expected_location = normalize(rows[i][2])
        expected_incident = normalize(rows[i][3])

        # Transcription
        start = time.time()
        with open(file_path, "rb") as audio_stream:
            transcript = transcribe_audio(audio_stream)
        process_time = time.time() - start

        # Metrics
        audio_length = get_audio_duration(file_path)
        rtf = compute_rtf(process_time, audio_length)
        transcript_norm = normalize(transcript)
        wer = jiwer.wer(reference, transcript_norm)

        # Semantic Extraction
        structured = extract_structured_data(transcript)
        eq = normalize(structured.get("equipment", ""))
        loc = normalize(structured.get("location_or_unit", ""))
        inc = normalize(structured.get("incident_summary", ""))

        correct = (
            eq == expected_equipment and
            loc == expected_location and
            inc == expected_incident
        )

        if correct:
            extraction_correct += 1

        total_wer += wer
        total_rtf += rtf
        status = "✓" if correct else "✗"

        print(f"{i+1:<6}{wer:<8.3f}{rtf:<8.3f}{status:<12}")

    # Results calculation
    n = len(audio_files)
    if n > 0:
        avg_wer = total_wer / n
        avg_rtf = total_rtf / n
        extraction_acc = extraction_correct / n

        print("\nFINAL RESULTS\n")
        print("Average WER:", round(avg_wer, 3))
        print("Average RTF:", round(avg_rtf, 3))
        print("Extraction Accuracy:", round(extraction_acc * 100, 2), "%")
    else:
        print("No audio files found for evaluation.")

if __name__ == "__main__":
    main()