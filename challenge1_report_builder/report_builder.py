# report_builder.py — Automated Client Report Builder
# Reads client data from CSV, generates reports with Claude,
# saves one report file per client
# Python 3.12 | Anthropic SDK 0.40.0

import csv
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Load .env from the same folder as this script
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# Configuration — using absolute paths based on script location
CSV_FILE = BASE_DIR / "clients.csv"
REPORTS_FOLDER = BASE_DIR / "reports"
MODEL = "claude-sonnet-4-5"

client = Anthropic()


def read_client_data(filepath: str) -> list[dict]:
    """Read all client rows from the CSV file.
    Returns a list of dictionaries — one per client."""
    clients = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clients.append(dict(row))
    print(f"Read {len(clients)} clients from {filepath}")
    return clients


def build_prompt(client_data: dict) -> str:
    """Build the Claude prompt for one client.
    Uses f-strings to embed the client's actual data."""
    return f"""You are a professional account manager writing a weekly
performance report for a client. Use clear, confident language.
Explain what the numbers mean — not just what they are.
Reference the notes to make the report feel personal.

Client: {client_data['client_name']} at {client_data['company']}

This week's performance:
- Tasks completed: {client_data['tasks_completed']} (target: {client_data['tasks_target']})
- Revenue this week: KES {client_data['revenue_this_week']}
- Revenue last week: KES {client_data['revenue_last_week']}
- New leads generated: {client_data['new_leads']}
- Support tickets resolved: {client_data['tickets_resolved']}
- Tickets still open: {client_data['tickets_open']}
- Context: {client_data['notes']}

Write a weekly report with these 4 sections:
1. Performance Summary (2 sentences — overall how did this week go)
2. Key Achievement (1 specific highlight with the actual number)
3. Area of Focus (1 specific thing that needs attention and why)
4. Next Week Priority (1 concrete action to take)

Be specific. Every sentence must add value. No filler."""


def generate_report(client_data: dict) -> str:
    """Call Claude to generate the report for one client.
    Returns the report text as a string."""
    name = client_data["client_name"]
    print(f"  Generating report for {name}...")

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": build_prompt(client_data)
            }]
        )
        return response.content[0].text

    except Exception as e:
        error_msg = f"ERROR generating report for {name}: {str(e)}"
        print(error_msg)
        return error_msg


def save_report(client_data: dict, report_text: str) -> str:
    """Save the generated report to a text file.
    Returns the filepath where it was saved."""
    # Create a clean filename from client name
    name_clean = client_data["client_name"].replace(" ", "_").lower()
    week = datetime.now().strftime("%Y-%m-%d")
    filename = f"{REPORTS_FOLDER}/{name_clean}_report_{week}.txt"

    # Build the full report with a header
    header = f"""WEEKLY PERFORMANCE REPORT
Client: {client_data['client_name']} — {client_data['company']}
Generated: {datetime.now().strftime('%A %d %B %Y at %H:%M')}
{'='*60}

"""
    full_report = header + report_text

    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"  Saved: {filename}")
    return filename


def main():
    """Main pipeline — reads CSV, generates and saves all reports."""
    print("=== Automated Report Builder Starting ===")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")

    # Make sure reports folder exists
    Path(REPORTS_FOLDER).mkdir(exist_ok=True)

    # Read all clients from CSV
    clients = read_client_data(CSV_FILE)

    # Track results
    results = []

    # Process each client
    print(f"Processing {len(clients)} clients...\n")
    for client_data in clients:
        report_text = generate_report(client_data)
        filepath = save_report(client_data, report_text)
        results.append({
            "client": client_data["client_name"],
            "company": client_data["company"],
            "report_file": filepath,
            "status": "error" if "ERROR" in report_text else "success"
        })

    # Print final summary
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"\n=== Complete ===")
    print(f"Reports generated: {successful}/{len(clients)}")
    print(f"Saved to: {REPORTS_FOLDER}/ folder")

    # Save a summary JSON log
    log_file = f"reports/run_log_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Run log saved: {log_file}")


if __name__ == "__main__":
    main()
