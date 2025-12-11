
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal, List, Dict, Any
import re

from app.core.config import settings
from app.services.embedding_service import search_chunks

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

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

# ---------------------------------------------------------
# UPDATE: Refined Prompt Template
# ---------------------------------------------------------
system_instructions = (
    "You are a concise news assistant. Use the following rules:\n"
    "1. AUTHORITY: Answer using ONLY the provided 'Context'. Do not use outside knowledge. "
    "If the answer is not in the Context, say: 'I don't have information on that in the current news.'\n"
    "2. FORMATTING: "
    "If asked for 'latest' or 'top' news, provide a numbered list: [Headline] - [1-sentence summary]. "
    "Keep standard answers concise and token-efficient.\n"
    "3. CONVERSATION: "
    "Resolve references (e.g., 'the first one', 'details on that') using the 'History'. "
    "Handle greetings (e.g., 'Hi') briefly and politely, then ask how you can help with the news."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instructions),
    MessagesPlaceholder(variable_name="history"),
    ("human", "Question: {question}\n\nContext:\n{context}")
])
# ---------------------------------------------------------


# ------------------- Pydantic Models --------------------

class ChatRequest(BaseModel):
    question: str
    mode: Literal["global", "local"] = "global"
    article_id: Optional[str] = None
    history: List[Dict[str, str]] = []

class ChatSource(BaseModel):
    article_id: str
    slug: Optional[str] = None
    category_id: Optional[int] = None
    snippet: str
    score: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]


# ------------------------- Helpers -------------------------

GREETING_PATTERN = re.compile(r"^\s*(hi|hello|hey|good morning|good afternoon|good evening)\b[!.?]?\s*$", re.IGNORECASE)

def is_greeting(text: str) -> bool:
    return bool(GREETING_PATTERN.match(text.strip()))

def is_latest_request(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in ("latest", "recent", "today", "today's news", "top news"))

def extract_answer_from_result(result):
    if hasattr(result, "content"):
        return result.content
    if hasattr(result, "text"):
        return result.text
    if isinstance(result, dict):
        for k in ("content", "text", "answer"):
            if k in result:
                return result[k]
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
            answer="Hello! I am your news assistant. How can I help you check the headlines today?",
            sources=[]
        )

    # 2) Retrieve vector search docs
    try:
        # Pre-process query for 'latest' intent to ensure semantic search hits relevant dates/topics
        search_query = question if not is_latest_request(question) else "latest top news headlines"
        
        docs = search_chunks(
            query=search_query,
            mode=payload.mode,
            article_id=payload.article_id,
            k=5 
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"search failed: {e}")

    # Fallback if no docs
    if not docs:
        return ChatResponse(
            answer="I searched the latest feed but couldn't find any relevant news stories right now.",
            sources=[]
        )

    # Build context
    context = "\n\n".join(d.page_content for d in docs if getattr(d, "page_content", None))
    if not context.strip():
        return ChatResponse(
            answer="I searched the latest feed but couldn't find any relevant news content.",
            sources=[]
        )

    # Convert frontend history to LangChain messages
    history_messages = []
    for msg in payload.history:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            history_messages.append(HumanMessage(content=content))
        elif role in ["assistant", "bot"]:
            history_messages.append(AIMessage(content=content))

    # Run LangChain Groq LLM
    try:
        chain = prompt | llm
        raw_result = chain.invoke({
            "question": question,
            "context": context,
            "history": history_messages
        })
        answer = extract_answer_from_result(raw_result)
        if not isinstance(answer, str):
            answer = str(answer)
    except Exception as e:
        print(f"LLM Error: {e}")
        answer = "I'm sorry, I'm having trouble processing that right now."

    # Build sources
    srcs: List[ChatSource] = []
    for d in docs:
        m = getattr(d, "metadata", None) or {}
        score = None
        if hasattr(d, "score"):
            try:
                score = float(d.score)
            except Exception:
                score = None
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