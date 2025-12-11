from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Literal, List
from groq import Groq
from app.core.config import settings
from app.services.embedding_service import search_chunks


router = APIRouter(prefix="/chat", tags=["chat"])

GROQ_API_KEY = settings.GROQ_API_KEY
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY required")

GROQ_MODEL = settings.GROQ_MODEL
_client = Groq(api_key=GROQ_API_KEY)


class ChatRequest(BaseModel):
    question: str
    mode: Literal["global", "local"] = "global"
    article_id: Optional[str] = None

class ChatSource(BaseModel):
    article_id: str
    slug: Optional[str] = None
    category_id: Optional[int] = None
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    if payload.mode == "local" and not payload.article_id:
        raise HTTPException(status_code=400, detail="article_id required for local")

    try:
        docs = search_chunks(
            query=payload.question,
            mode=payload.mode,
            article_id=payload.article_id,
            k=4
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"search failed: {e}")

    context = "\n\n".join(
        f"{d.page_content}" for d in docs
    ) if docs else ""

    system_msg = (
        "ONLY answer using the information in context. "
        "If answer not found, say you don't know."
    )
    user_msg = f"Question: {payload.question}\n\nContext:\n{context}"

    try:
        comp = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.1,
        )
        answer = comp.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM failed: {e}")

    srcs = []
    for d in docs:
        m = d.metadata or {}
        srcs.append(ChatSource(
            article_id=str(m.get("article_id")),
            slug=m.get("slug"),
            category_id=m.get("category_id"),
            snippet=d.page_content[:200]
        ))

    return ChatResponse(answer=answer, sources=srcs)
