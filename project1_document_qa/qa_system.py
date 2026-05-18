import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from dotenv import load_dotenv
from pathlib import Path
import os
qa_chain = None
retriever = None

load_dotenv(Path(__file__).parent / ".env")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

DOCS_DIR = Path(__file__).parent / "documents"
CHROMA_DIR = Path(__file__).parent / "chroma_db"


def load_documents():
    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} document(s)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        print("Loading existing vector store from disk...")
        vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embedding_model
        )
    else:
        print("Building vector store for the first time...")
        chunks = load_documents()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=str(CHROMA_DIR)
        )
        print("Vector store saved to disk")

    return vectorstore


def build_qa_chain(vectorstore):
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        anthropic_api_key=ANTHROPIC_API_KEY,
        temperature=0
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    prompt = ChatPromptTemplate.from_template("""
Answer the question using only the context below.
If the answer is not in the context, say "I could not find that in the documents."

Context:
{context}

Question: {question}
""")

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever


app = FastAPI()
qa_chain = None


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    source: str


@app.on_event("startup")
async def startup():
    global qa_chain, retriever
    vectorstore = get_vectorstore()
    qa_chain, retriever = build_qa_chain(vectorstore)
    print("RAG system ready")


@app.get("/")
def health():
    return {"status": "running", "system": "Document Q&A RAG"}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    docs = retriever.invoke(request.question)
    answer = qa_chain.invoke(request.question)
    source = docs[0].page_content[:300] if docs else "No source found"
    return AnswerResponse(answer=answer, source=source)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
