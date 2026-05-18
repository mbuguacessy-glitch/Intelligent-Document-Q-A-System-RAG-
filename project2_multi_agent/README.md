# Multi-Agent Research System

## What this does
A Python system with three AI agents working in sequence to produce
a fully researched, written, and reviewed report on any topic. The
Researcher searches the web for current information, the Writer turns
the findings into a structured report, and the Reviewer scores the
quality and identifies improvements. Exposed as a FastAPI HTTP endpoint
so any tool can trigger a full research pipeline with one POST request.

## The problem it solves
Complex research tasks require multiple specialist steps that no single
AI call handles well. Research, writing, and quality review are three
fundamentally different jobs. When you send a complex question to a
single AI prompt you get one pass with no review. This system uses
three specialist agents — each with its own role and instructions —
producing a dramatically better result than any single agent could.

## Measurable result
- Research pipeline completion time: 30 to 60 seconds
- Agents in the pipeline: 3 (Researcher, Writer, Reviewer)
- Claude API calls per request: 3
- Output sections per report: research notes, full report, editorial review
- Quality score returned: yes — out of 10 with specific improvements listed
- Report saved as timestamped .txt file: yes

## Tech stack — 2026 versions
- Python 3.12.0
- Anthropic SDK 0.40+
- Claude claude-sonnet-4-6
- Tavily Search API (free tier)
- FastAPI + Uvicorn
- python-dotenv
- Pydantic v2

## Tools used and why

### Claude API — the intelligence behind all three agents
The same Claude model powers all three agents with different system
prompts. One prompt makes it a researcher, another a writer, another
a reviewer. The instructions define the role — the model provides
the intelligence.

### Tavily Search API — live web access for the Researcher
Gives the Researcher agent access to current web search results.
Without Tavily, Claude would only use its training data which has
a knowledge cutoff. Tavily returns clean structured results Claude
can read and synthesise directly.

### FastAPI — the API layer
Exposes the full three-agent pipeline as a single HTTP endpoint.
Send a topic to POST /research and receive the complete research
notes, report, and editorial review. Callable from n8n, Make.com,
or any HTTP client.

### pathlib + datetime — report file management
Saves every completed report as a uniquely timestamped .txt file
in the reports/ folder. Every run produces a new file so no report
is ever overwritten.

### python-dotenv — key management
Loads both the Anthropic and Tavily API keys from .env so neither
is hardcoded in the script or exposed when pushing to GitHub.

## How it works
1. POST request arrives at /research with a topic
2. Researcher agent calls Tavily to search the web for current information
3. Tavily returns the 5 most relevant results
4. Researcher synthesises findings into structured research notes
5. Writer receives the research notes and produces a structured report
6. Reviewer receives the report and returns a quality score and improvements
7. Full output saved as a timestamped .txt file in reports/
8. Response returned with report, review, and file path

## The three agents

### Agent 1 — Researcher
Receives: a topic
Does: searches the web via Tavily, reads results, extracts key facts
Returns: structured research notes with Key Facts, Statistics, Trends,
and Sources sections

### Agent 2 — Writer
Receives: research notes from Agent 1
Does: structures information into a formal report
Returns: complete report with Executive Summary, Background, Key
Findings, Analysis, and Conclusion

### Agent 3 — Reviewer
Receives: the written report from Agent 2
Does: evaluates accuracy, completeness, structure, and clarity
Returns: quality score out of 10, strengths, gaps found, improvement
suggestions, and a publish recommendation

## Error handling
- ModuleNotFoundError tavily — run pip install tavily-python
- Tavily API key invalid — check .env has TAVILY_API_KEY with no spaces
- Port 8001 in use — run netstat -ano | findstr :8001 then
  taskkill /PID [id] /F
- Request times out — normal for 30-60 seconds, do not cancel
- Report truncated in terminal — open the saved .txt file in VS Code
  or use Select-Object -ExpandProperty report
- Thin research results — use a more specific topic and increase
  max_results from 5 to 8 in the Tavily search call

## Screenshots
[https://imgur.com/TGO0xO1]
[https://imgur.com/P1yzWHD]
[https://imgur.com/undefined]
[https://imgur.com/undefined]
[https://imgur.com/undefined]
