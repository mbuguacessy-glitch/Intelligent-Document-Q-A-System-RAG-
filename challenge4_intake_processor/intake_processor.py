import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from pyairtable import Api
from pydantic import BaseModel, field_validator

load_dotenv(Path(__file__).parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE_NAME", "Leads")


class ClientIntake(BaseModel):
    client_name:      str
    email:            str
    project_type:     str
    budget:           float
    timeline:         str
    key_requirements: str
    urgency_level:    str

    @field_validator("urgency_level")
    @classmethod
    def validate_urgency(cls, v):
        allowed = {"Low", "Medium", "High"}
        if v not in allowed:
            return "Medium"
        return v

  # Sends raw intake text to Claude and extracts structured client data as a validated ClientIntake object


def extract_intake_data(raw_text: str) -> ClientIntake:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are processing a client intake form for an AI automation agency.
Extract the following fields from this intake message.
Return ONLY a JSON object — no explanation, no markdown, no backticks.

Fields to extract:
- client_name: Full name of the person
- email: Their email address
- project_type: What type of automation they need (1 sentence)
- budget: Numeric value only (convert to USD if another currency, use 0 if unclear)
- timeline: How soon they need it (e.g. "6 weeks", "3 months", "no rush")
- key_requirements: A clean 2-3 sentence summary of what they need
- urgency_level: Exactly one of: Low, Medium, High

Intake message:
{raw_text}

Return ONLY valid JSON:"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_json = message.content[0].text.strip()
    data = json.loads(raw_json)
    return ClientIntake(**data)

# Takes a validated ClientIntake object and saves it as a new record in the Airtable Leads table


def save_to_airtable(intake: ClientIntake, raw_text: str) -> str:
    api = Api(AIRTABLE_TOKEN)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)

    record = table.create({
        "Client Name":      intake.client_name,
        "Email":            intake.email,
        "Project Type":     intake.project_type,
        "Budget":           intake.budget,
        "Timeline":         intake.timeline,
        "Key Requirements": intake.key_requirements,
        "Urgency Level":    intake.urgency_level,
        "Status":           "New",
        "Raw Input":        raw_text,
        "Processed At":     datetime.today().strftime("%Y-%m-%d"),
    })

    return record["id"]

# Loops through every .txt file in the sample_intakes folder, extracts data with Claude, and saves each one to Airtable


def process_intake_folder():
    intakes_folder = Path(__file__).parent / "sample_intakes"
    txt_files = list(intakes_folder.glob("*.txt"))

    if not txt_files:
        print("No intake files found in sample_intakes/")
        return

    print(f"Found {len(txt_files)} intake file(s) to process\n")

    for file in txt_files:
        print(f"Processing: {file.name}")
        raw_text = file.read_text(encoding="utf-8")

        print("  → Sending to Claude for extraction...")
        intake = extract_intake_data(raw_text)
        print(
            f"  ✓ Extracted: {intake.client_name} | {intake.project_type} | {intake.urgency_level} urgency")

        print("  → Saving to Airtable...")
        record_id = save_to_airtable(intake, raw_text)
        print(f"  ✓ Saved. Airtable record ID: {record_id}\n")

    print("All intakes processed successfully.")


if __name__ == "__main__":
    process_intake_folder()
