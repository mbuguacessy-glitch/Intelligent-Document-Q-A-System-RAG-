import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from tavily import TavilyClient
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

load_dotenv(Path(__file__).parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def researcher_agent(topic: str) -> str:
    print(f"  Researcher searching: {topic}")

    search_results = tavily_client.search(
        query=topic,
        max_results=5
    )

    results_text = ""
    for r in search_results["results"]:
        results_text += f"Source: {r['url']}\n"
        results_text += f"Content: {r['content']}\n\n"

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="""You are a research specialist. Your job is to read 
web search results and extract the most important facts, statistics, 
trends, and insights on the given topic. Return structured research 
notes with clear sections: Key Facts, Statistics, Trends, and Sources.""",
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}\n\nSearch Results:\n{results_text}\n\nProvide structured research notes."
        }]
    )

    return message.content[0].text


def writer_agent(topic: str, research_notes: str) -> str:
    print("  Writer drafting report...")

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system="""You are a professional report writer. Your job is to 
take research notes and write a polished, structured report. Use clear 
headings: Executive Summary, Background, Key Findings, Analysis, and 
Conclusion. Write in a professional tone. Be specific and use the data 
from the research notes.""",
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}\n\nResearch Notes:\n{research_notes}\n\nWrite a complete professional report."
        }]
    )

    return message.content[0].text


def reviewer_agent(topic: str, report: str) -> str:
    print("  Reviewer evaluating report...")

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system="""You are a senior editor and quality reviewer. Evaluate 
reports on these criteria: accuracy, completeness, structure, and clarity.
Return your review in this exact format:
QUALITY SCORE: X/10
STRENGTHS: [list 2-3 strengths]
GAPS FOUND: [list any missing information or weak sections]
IMPROVEMENTS: [list 2-3 specific actionable improvements]
RECOMMENDATION: [Publish / Revise / Major revision needed]""",
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}\n\nReport to review:\n{report}\n\nProvide your editorial review."
        }]
    )

    return message.content[0].text


def run_research_pipeline(topic: str) -> dict:
    print(f"\nStarting research pipeline for: {topic}")

    research = researcher_agent(topic)
    print("  Research complete")

    report = writer_agent(topic, research)
    print("  Report written")

    review = reviewer_agent(topic, report)
    print("  Review complete")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.txt"
    filepath = REPORTS_DIR / filename

    full_output = f"""TOPIC: {topic}
GENERATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*60}

RESEARCH NOTES
{'='*60}
{research}

FULL REPORT
{'='*60}
{report}

EDITORIAL REVIEW
{'='*60}
{review}
"""
    filepath.write_text(full_output, encoding="utf-8")
    print(f"  Saved to: {filepath}")

    return {
        "topic": topic,
        "research": research,
        "report": report,
        "review": review,
        "saved_to": str(filepath)
    }


app = FastAPI()


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    topic: str
    report: str
    review: str
    saved_to: str


@app.get("/")
def health():
    return {"status": "running", "system": "Multi-Agent Research System"}


@app.post("/research", response_model=ResearchResponse)
async def research_topic(request: ResearchRequest):
    result = run_research_pipeline(request.topic)
    return ResearchResponse(
        topic=result["topic"],
        report=result["report"],
        review=result["review"],
        saved_to=result["saved_to"]
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
