# Automated Client Intake Processor

## What this does
A Python script that reads raw client intake submissions, extracts structured data using Claude AI, validates every field with Pydantic, and saves clean records to Airtable automatically. Eliminates manual reading and CRM data entry for client intake forms.

## The problem it solves
Agencies receive intake forms as unstructured text. Someone has to manually read each one, extract the budget, timeline, and requirements, then create a CRM record. For 50+ clients a week this becomes a part-time job. This script processes any number of intake files in seconds with no human involvement.

## Measurable result
- Processing time: under 5 seconds per intake (including Claude API call and Airtable save)
- Intake files processed: 2 (intake_001.txt and intake_002.txt)
- Fields extracted per record: 7
- Records successfully saved to Airtable: yes
- Pydantic validation: active — invalid urgency values auto-corrected to Medium

## Tech stack — 2026 versions
- Python 3.12.0
- Anthropic SDK 0.40+
- Claude claude-sonnet-4-6
- Pydantic v2
- pyairtable 2.x
- python-dotenv

## How it works
1. Script scans the sample_intakes/ folder for all .txt files
2. Reads each file as raw unstructured text
3. Sends the text to Claude with a structured extraction prompt
4. Claude returns a JSON object with exactly 7 fields
5. Pydantic validates each field — wrong types or invalid values caught before saving
6. pyairtable writes the clean record to the Leads table in Airtable
7. Script prints the Airtable record ID as confirmation and moves to the next file

## Airtable fields populated
- Client Name — extracted by Claude
- Email — extracted by Claude
- Project Type — extracted by Claude
- Budget — numeric value only, extracted by Claude
- Timeline — extracted by Claude
- Key Requirements — 2-3 sentence summary, extracted by Claude
- Urgency Level — Low / Medium / High, validated by Pydantic
- Status — set to "New" automatically
- Raw Input — original intake text saved for reference
- Processed At — today's date set automatically

## How to run
Add new intake files to sample_intakes/ as .txt files — the script processes all of them automatically.

## Error handling
- Missing API key — check .env file has no spaces around = signs
- Claude returns non-JSON — add print(raw_json) before json.loads() to see raw output
- Invalid urgency value — Pydantic @field_validator auto-corrects to Medium
- Airtable UNKNOWN_FIELD_NAME — field name in code does not match Airtable column exactly
- Airtable 404 NOT_FOUND — regenerate token at airtable.com/create/tokens with correct scopes
- AIRTABLE_BASE_ID reads as None — check all four keys are saved in the .env file

## Screenshots
[https://imgur.com/GxIyFgN]
[https://imgur.com/zrfBOad]

## Part of
AI Automation Learning Roadmap — Phase 2 Python Challenges
Focus: AI integration and automation (no-code to code bridge)

- Challenge 1 — Automated Report Builder
- Challenge 2 — Document Classifier
- Challenge 3 — n8n to Python Bridge
- Challenge 4 — Client Intake Processor ← you are here
- Challenge 5 — Coming up