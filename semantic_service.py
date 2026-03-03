import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def extract_structured_data(transcript):

    prompt = f"""
Extract structured incident report data from the transcript.

Return ONLY JSON in this format:

{{
  "equipment": "",
  "incident_summary": "",
  "location_or_unit": "",
  "incident_date": "",
  "incident_time": "",
  "severity": ""
}}

Rules:
- equipment = affected machine/device
- incident_summary = what happened
- location_or_unit = where it happened
- incident_date = date if mentioned
- incident_time = time if mentioned
- severity = Low, Medium, High if obvious
- If not mentioned, return empty string.

Transcript:
"{transcript}"
"""

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt
    )

    raw_output = response.output_text.strip()

    try:
        structured_json = json.loads(raw_output)
    except json.JSONDecodeError:
        structured_json = {
            "equipment": "",
            "incident_summary": "",
            "location_or_unit": "",
            "incident_date": "",
            "incident_time": "",
            "severity": ""
        }

    return structured_json