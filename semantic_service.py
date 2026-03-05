import re
from datetime import datetime


EQUIPMENTS = {
    "pump",
    "motor",
    "compressor",
    "valve",
    "boiler",
    "generator",
    "turbine",
    "fan",
    "conveyor",
    "reactor"
}


INCIDENT_MAP = {

    "overheat": "overheating",
    "overheated": "overheating",
    "overheating": "overheating",

    "leak": "leak",
    "leaking": "leak",
    "leaked": "leak",

    "failure": "failure",
    "failed": "failure",

    "malfunction": "malfunction",
    "malfunctioning": "malfunction",

    "breakdown": "breakdown",
    "broken": "breakdown",

    "smoke": "smoke",
    "smoking": "smoke",

    "vibration": "vibration",
    "vibrating": "vibration",

    "shutdown": "shutdown",

    "blockage": "blockage",
    "blocked": "blockage"
}


SEVERITY = {
    "minor",
    "major",
    "critical"
}


def extract_equipment(text):

    words = text.split()

    for word in words:
        if word in EQUIPMENTS:
            return word

    return ""


def extract_incident(text):

    words = text.split()

    for word in words:

        if word in INCIDENT_MAP:
            return INCIDENT_MAP[word]

    return ""


def extract_location(text):

    match = re.search(r"unit\s*\d+", text)

    if match:
        return match.group()

    return ""


def extract_time(text):

    match = re.search(r"\d{1,2}\s*(am|pm)", text)

    if match:
        return match.group()

    return ""


def extract_severity(text):

    words = text.split()

    for word in words:

        if word in SEVERITY:
            return word

    return ""


def extract_temperature(text):

    match = re.search(r"\d+\s*degree", text)

    if match:
        return match.group()

    return ""


def extract_structured_data(text):

    text = text.lower()

    data = {

        "reporter_name": "",

        "department": "",

        "equipment": extract_equipment(text),

        "incident_summary": extract_incident(text),

        "location_or_unit": extract_location(text),

        "incident_date": datetime.now().strftime("%Y-%m-%d"),

        "incident_time": extract_time(text),

        "severity": extract_severity(text),

        "measured_parameters": extract_temperature(text),

        "remarks": ""
    }

    return data