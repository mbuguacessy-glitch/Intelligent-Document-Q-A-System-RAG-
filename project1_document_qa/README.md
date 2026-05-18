# Intelligent Document Q&A System (RAG)

## What this does
A Python system that reads documents, converts them into searchable
vectors using embeddings, stores them in ChromaDB, and answers plain
English questions about them accurately — citing exactly where each
answer came from. Exposed as a FastAPI HTTP endpoint so any tool
can query your documents via API.

## The problem it solves
Businesses have knowledge locked in documents nobody can search
efficiently. Finding an answer in a 50-page policy document takes
20 minutes manually. This system answers any question about any
document in under 3 seconds — and tells you exactly which part of
the document the answer came from.

## Measurable result
- Questions answered correctly from document: yes
- Hallucination on unknown topics: none — returns "I could not
  find that in the documents"
- Vector store persistence: confirmed — second run loads from disk
  instantly without reprocessing
- Source citations: included in every response
- API endpoint: live on http://localhost:8000/ask

## Tech stack — 2026 versions
- Python 3.12.0
- LangChain 1.3 + LangChain Community 0.4
- ChromaDB — persistent vector store
- HuggingFace sentence-transformers/all-MiniLM-L6-v2
- Claude claude-sonnet-4-6
- FastAPI + Uvicorn
- python-dotenv

## Tools used and why

### LangChain — the pipeline orchestrator
Connects document loading, text splitting, embedding, vector storage,
and Claude into one chain. Without LangChain you would manually write
all the handoffs between each tool.

### ChromaDB — the vector database
Stores all document chunks as vectors on disk. Finds the most
semantically relevant chunks when a question comes in. Persistent —
documents are processed once and queries run instantly on every
subsequent run.

### HuggingFace Embeddings — the meaning converter
Converts each text chunk into a list of numbers representing its
meaning. Runs locally with no API key and no cost. Makes it possible
to search by meaning instead of exact words.

### Claude API — the answer writer
Reads the retrieved chunks and writes a precise grounded answer.
Instructed to only use provided context — no hallucination from
outside training data.

### FastAPI — the API layer
Exposes the entire RAG system as an HTTP endpoint. Any tool —
n8n, Make.com, a web app — can query your documents by sending
a POST request to /ask.

## How it works
1. DirectoryLoader reads all .txt files from the documents/ folder
2. RecursiveCharacterTextSplitter cuts each document into 500
   character chunks with 50 character overlap
3. HuggingFace embedding model converts each chunk into a vector
4. ChromaDB stores all vectors and original text on disk
5. FastAPI server starts and loads the vector store
6. User sends a question to POST /ask
7. Question converted to a vector and matched against ChromaDB
8. Top 3 most relevant chunks retrieved
9. Claude reads chunks and writes a grounded answer
10. Answer and source chunk returned in the response

## Adding your own documents
Drop any .txt file into the documents/ folder. Delete the chroma_db/
folder to force reprocessing. Restart the server — it will rebuild
the vector store with your new documents automatically.

## Error handling
- ModuleNotFoundError — run pip install langchain langchain-community
  langchain-anthropic langchain-text-splitters chromadb
  sentence-transformers fastapi uvicorn
- No documents found — confirm .txt files are in documents/ folder
- AuthenticationError — check ANTHROPIC_API_KEY in .env has no spaces
- Slow first run — embedding model downloading (80MB, happens once only)
- Port 8000 in use — run netstat -ano | findstr :8000 then
  taskkill /PID [id] /F
- Wrong answers — delete chroma_db/ folder and restart to rebuild
  vectors from scratch

## Screenshots
[https://imgur.com/Rr0LTSE]
[https://imgur.com/srqdsBF]
[https://imgur.com/fbe72a6]

