import json
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MANDATORY_FIELDS = ["equipment", "location_or_unit", "incident_summary"]


def fast_rule_parser(text):

    text = text.lower()
    result = {}

    equipment_list = [
        "motor","pump","valve","compressor","fan",
        "boiler","generator","conveyor","turbine","filter"
    ]

    for eq in equipment_list:
        if eq in text:
            result["equipment"] = eq
            break

    unit_match = re.search(r"unit\s*\d+", text)
    if unit_match:
        result["location_or_unit"] = unit_match.group()

    if "overheat" in text or "heat" in text:
        result["incident_summary"] = "overheating"

    elif "leak" in text:
        result["incident_summary"] = "leakage"

    elif "malfunction" in text:
        result["incident_summary"] = "malfunction"

    if "severe" in text or "critical" in text:
        result["severity"] = "High"

    elif "major" in text:
        result["severity"] = "Medium"

    elif "minor" in text:
        result["severity"] = "Low"

    return result


def llm_extract(transcript):

    prompt = f"""
Extract incident report fields as JSON.

Fields:
reporter_name
department
equipment
incident_summary
location_or_unit
incident_date
incident_time
severity
measured_parameters
remarks

Text:
{transcript}
"""

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt,
        temperature=0,
        max_output_tokens=120
    )

    raw = response.output_text.strip()

    try:
        return json.loads(raw)
    except:
        return {}


def extract_structured_data(transcript):

    result = {
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

    rule_data = fast_rule_parser(transcript)

    for k,v in rule_data.items():
        result[k] = v

    if all(result[field] for field in MANDATORY_FIELDS):
        return result

    llm_data = llm_extract(transcript)

    for k,v in llm_data.items():
        if v and not result.get(k):
            result[k] = v

    return result