# Intelligent Document Q&A System (RAG)

A production RAG pipeline that answers questions from documents in under 3 seconds with source citations. Deployed live on Render and callable 24/7 from anywhere.

---

## The Problem It Solves

Research and document review takes 15-20 minutes per document manually. A lawyer reading a contract, an analyst reviewing a report, a doctor checking patient history — all spending time reading when they should be deciding.

This system cuts document research from 20 minutes to under 3 seconds.

---

## How It Works
Document uploaded
↓
Split into chunks and embedded into ChromaDB vector database
↓
User asks a question
↓
Semantic search finds the most relevant chunks
↓
Claude answers using only the retrieved context
↓
Answer returned with source citations

---

## Key Features

- **Grounded answers** — Claude answers only from document context, never hallucinates
- **Source citations** — every answer includes which part of the document it came from
- **Fast retrieval** — semantic search finds relevant chunks in milliseconds
- **Production deployed** — live 24/7 on Render, no local setup needed
- **RAGAS evaluation** — faithfulness score of 0.92 measured using Claude as judge

---

## Tech Stack

- **FastAPI** — API framework
- **LangChain** — document loading, chunking, retrieval chain
- **ChromaDB** — vector database for semantic search
- **Claude API** — answer generation and evaluation
- **Render** — cloud deployment

---

## Live Demo

API is live at: [ai-agent-api-w7uh.onrender.com](https://ai-agent-api-w7uh.onrender.com)

---

## Measurable Outcome

| Metric | Before | After |
|--------|--------|-------|
| Document research time | 20 minutes | Under 3 seconds |
| Answer accuracy (faithfulness) | Manual review | 0.92 RAGAS score |
| Availability | Office hours only | 24/7 |