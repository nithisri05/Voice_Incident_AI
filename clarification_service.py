import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def generate_clarification_question(transcript, structured):

    prompt = f"""
You are an industrial incident reporting assistant.

The structured report below is missing mandatory fields.

Structured Report:
{structured}

Transcript:
"{transcript}"

Mandatory fields:
- equipment
- incident_summary
- location_or_unit
- incident_date
- incident_time

Ask ONE short clarification question for the MOST important missing field.
Do not ask multiple questions.
Return only the question.
"""

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt
    )

    return response.output_text.strip()