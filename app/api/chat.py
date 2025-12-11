# app/api/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal, List
import re

from app.core.config import settings
from app.services.embedding_service import search_chunks

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

router = APIRouter(prefix="/chat", tags=["chat"])

# env
GROQ_API_KEY = settings.GROQ_API_KEY
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY required")

GROQ_MODEL = settings.GROQ_MODEL

# LangChain LLM
llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.1,
)

# Prompt template (replaces manual messages array)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "ONLY answer using the provided context.\n"
     "If the answer is not in the context, say you don't know."
    ),
    ("human",
     "Question: {question}\n\nContext:\n{context}"
    )
])


# ------------------- Pydantic Models --------------------

class ChatRequest(BaseModel):
    question: str
    mode: Literal["global", "local"] = "global"
    article_id: Optional[str] = None

class ChatSource(BaseModel):
    article_id: str
    slug: Optional[str] = None
    category_id: Optional[int] = None
    snippet: str
    score: Optional[float] = None  # optional, non-breaking for frontend

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]


# ------------------------- Helpers -------------------------

GREETING_PATTERN = re.compile(r"^\s*(hi|hello|hey|good morning|good afternoon|good evening)\b[!.?]?\s*$", re.IGNORECASE)

def is_greeting(text: str) -> bool:
    return bool(GREETING_PATTERN.match(text.strip()))

def is_latest_request(text: str) -> bool:
    # simple heuristic: contains 'latest' or 'recent' or 'today's news'
    t = text.lower()
    return any(k in t for k in ("latest", "recent", "today", "today's news", "top news"))

def extract_answer_from_result(result):
    # Robust extraction for different possible LangChain/Groq shapes
    # prefer .content, then .text, then key 'content' in dict, else fallback to str(result)
    if hasattr(result, "content"):
        return result.content
    if hasattr(result, "text"):
        return result.text
    if isinstance(result, dict):
        for k in ("content", "text", "answer"):
            if k in result:
                return result[k]
    # fallback
    return str(result)


# ------------------------- Endpoint -------------------------

@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    question = payload.question.strip()
    if payload.mode == "local" and not payload.article_id:
        raise HTTPException(status_code=400, detail="article_id required for local")

    # 1) Greeting short-circuit
    if is_greeting(question):
        return ChatResponse(
            answer="Hello. How can I help you with the news today?",
            sources=[]
        )

    # 2) Retrieve vector search docs (handle "latest" intent)
    try:
        # for 'latest' queries prefer the heuristic; search_chunks will try to sort by published_at if present.
        docs = search_chunks(
            query=question if not is_latest_request(question) else "latest news",
            mode=payload.mode,
            article_id=payload.article_id,
            k=5  # return 4-5 latest as requested
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"search failed: {e}")

    # If no docs found, do NOT call the LLM — return explicit 'I don't know'
    if not docs:
        return ChatResponse(
            answer="I don't know. No relevant news content found.",
            sources=[]
        )

    # Build context
    context = "\n\n".join(d.page_content for d in docs if getattr(d, "page_content", None))
    if not context.strip():
        return ChatResponse(
            answer="I don't know. No relevant news content found.",
            sources=[]
        )

    # Run LangChain Groq LLM
    try:
        chain = prompt | llm
        # .invoke may accept a dict; extract robustly
        raw_result = chain.invoke({"question": question, "context": context})
        answer = extract_answer_from_result(raw_result)
        # ensure string
        if not isinstance(answer, str):
            answer = str(answer)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM failed: {e}")

    # Build sources (include optional score if present)
    srcs: List[ChatSource] = []
    for d in docs:
        m = getattr(d, "metadata", None) or {}
        score = None
        # Some vectorstore objects attach a score attribute; try to extract it if present
        if hasattr(d, "score"):
            try:
                score = float(d.score)
            except Exception:
                score = None
        # Also support metadata-based score key
        if score is None and "score" in m:
            try:
                score = float(m.get("score"))
            except Exception:
                score = None

        srcs.append(ChatSource(
            article_id=str(m.get("article_id") or ""),
            slug=m.get("slug"),
            category_id=m.get("category_id"),
            snippet=(getattr(d, "page_content", "") or "")[:200],
            score=score
        ))

    return ChatResponse(answer=answer, sources=srcs)
