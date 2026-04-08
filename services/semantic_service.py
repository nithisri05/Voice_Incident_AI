import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

FIELDS = [
    "reporter_name",
    "department",
    "equipment",
    "incident_summary",
    "location_or_unit",
    "incident_date",
    "incident_time",
    "severity",
    "measured_parameters",
    "remarks"
]

EQUIPMENT_LIST = [
    "motor", "pump", "valve", "compressor",
    "fan", "boiler", "conveyor", "generator"
]

# ---------------- CONTEXT CORRECTION ----------------
def context_correct(text):
    prompt = f"""
Correct industrial speech-to-text errors ONLY if obvious.

Examples:
unix 6 → unit 6
motar → motor

Text:
{text}

Return corrected sentence only.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=prompt,
            temperature=0
        )
        return response.output_text.strip().lower()
    except:
        return text.lower()


# ---------------- RULE EXTRACTION (STRONG) ----------------
def extract_unit(text):
    match = re.search(r"(unit\s*\d+)", text)
    return match.group() if match else ""


def extract_department(text):
    match = re.search(r"(\w+\s*(department|dept))", text)
    return match.group() if match else ""


def extract_equipment(text):
    for eq in EQUIPMENT_LIST:
        if eq in text:
            return eq
    return ""


def extract_reporter(text):
    match = re.search(r"(this is|i am)\s+(\w+)", text)
    return match.group(2) if match else ""


# ---------------- INCIDENT DETECTION ----------------
def extract_incident(text):

    if "overheat" in text:
        return "overheating"

    if "malfunction" in text:
        return "malfunction"

    if "leak" in text:
        return "leak detected"

    return ""


# ---------------- SEVERITY ----------------
def infer_severity(text):

    if "severe" in text or "failure" in text:
        return "High"

    if "overheat" in text or "leak" in text:
        return "Medium"

    return "Low"


# ---------------- CONFIDENCE ----------------
def calculate_confidence(data):

    core_fields = [
        "equipment",
        "location_or_unit",
        "department",
        "incident_summary"
    ]

    filled = 0

    for f in core_fields:
        val = data.get(f, "")

        # 🔥 strict check (avoid fake/inferred values)
        if isinstance(val, str) and val.strip() != "":
            filled += 1

    score = int((filled / len(core_fields)) * 100)

    return score

# ---------------- SUGGESTION ----------------
def get_suggested_action(data):

    if not data.get("incident_summary"):
        return ""

    try:
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=f"Give one safety action for {data.get('incident_summary')}"
        )
        return response.output_text.strip()
    except:
        return ""


# ---------------- MAIN ----------------
def extract_structured_data(transcript, conversation_text=None):

    raw_text = conversation_text if conversation_text else transcript

    # 🔥 STEP 1: CONTEXT FIX (EARLY)
    text = context_correct(raw_text)

    # 🔥 STEP 2: RULE EXTRACTION (PRIMARY)
    data = {}

    data["location_or_unit"] = extract_unit(text)
    data["department"] = extract_department(text)
    data["equipment"] = extract_equipment(text)
    data["incident_summary"] = extract_incident(text)
    data["reporter_name"] = extract_reporter(text)

    # 🔥 STEP 3: FALLBACK LLM (ONLY IF NEEDED)
    if not data["equipment"] or not data["incident_summary"]:
        try:
            response = client.responses.create(
                model="gpt-4.1-nano",
                input=f"Extract equipment and incident from: {text}"
            )
            extra = response.output_text.lower()

            if not data["equipment"]:
                for eq in EQUIPMENT_LIST:
                    if eq in extra:
                        data["equipment"] = eq

            if not data["incident_summary"]:
                if "overheat" in extra:
                    data["incident_summary"] = "overheating"

        except:
            pass

    # 🔥 STEP 4: SEVERITY
    data["severity"] = infer_severity(text)

    # 🔥 STEP 5: CONFIDENCE
    data["confidence"] = calculate_confidence(data)

    # 🔥 STEP 6: ACTION
    data["suggested_action"] = get_suggested_action(data)

    return data