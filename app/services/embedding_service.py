# app/services/embedding_service.py
from typing import List, Optional, Literal
import threading

import cohere
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from app.core.config import settings

# env
COHERE_API_KEY = settings.COHERE_API_KEY
if not COHERE_API_KEY:
    raise RuntimeError("COHERE_API_KEY required")

COHERE_EMBED_MODEL = settings.COHERE_EMBED_MODEL
CHROMA_PERSIST_DIR = settings.CHROMA_PERSIST_DIR
CHROMA_COLLECTION_NAME = settings.CHROMA_COLLECTION_NAME

# splitter
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

# Reuse a single Cohere client for the process
_cohere_client = cohere.Client(COHERE_API_KEY)

def _embed_documents(texts: List[str]) -> List[List[float]]:
    # Use the single client instance
    resp = _cohere_client.embed(
        texts=texts,
        model=COHERE_EMBED_MODEL,
        input_type="search_document"
    )
    return resp.embeddings

def _embed_query(text: str) -> List[float]:
    resp = _cohere_client.embed(
        texts=[text],
        model=COHERE_EMBED_MODEL,
        input_type="search_query"
    )
    return resp.embeddings[0]


class CohereEmbeddingWrapper:
    def embed_documents(self, texts: List[str]):
        return _embed_documents(texts)

    def embed_query(self, text: str):
        return _embed_query(text)

# initialize chroma
_vectorstore = Chroma(
    collection_name=CHROMA_COLLECTION_NAME,
    embedding_function=CohereEmbeddingWrapper(),   # <-- wrapper instance
    persist_directory=CHROMA_PERSIST_DIR,
)

# a simple lock to reduce chance of concurrent delete/add races (not a full solution)
_index_lock = threading.Lock()

# we need manual add using embed_documents instead of embed_query
def add_chunks(texts: List[str], metadatas: List[dict], ids: List[str]):
    vecs = _embed_documents(texts)
    _vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids, embeddings=vecs)


# -------------------------- public helpers --------------------------

def build_document_text(article):
    parts = []
    if getattr(article, "title", None):
        parts.append(article.title)
    if getattr(article, "summary", None):
        parts.append(article.summary)
    if getattr(article, "content", None):
        parts.append(article.content)
    return "\n\n".join(p for p in parts if p)


def delete_article_chunks(article_id: str):
    # remove chunks by metadata filter
    _vectorstore.delete(where={"article_id": article_id})


def index_article(article):
    """
    Index an article:
    - builds text
    - splits into chunks
    - deletes existing chunks for that article
    - adds new chunks
    Note: a simple lock is used to reduce race conditions; for high concurrency,
    push indexing to a single-threaded worker queue (recommended).
    """
    text = build_document_text(article)
    if not text or not text.strip():
        delete_article_chunks(str(article.id))
        return

    chunks = _splitter.split_text(text)

    ids = [f"{article.id}:{i}" for i in range(len(chunks))]
    metas = [{
        "article_id": str(article.id),
        "slug": getattr(article, "slug", None),
        "category_id": getattr(article, "category_id", None),
        "status": article.status.value if hasattr(article.status, "value") else str(getattr(article, "status", "")),
        # Optionally include published_at in metadata if your Article model provides it:
        **({"published_at": getattr(article, "published_at")} if getattr(article, "published_at", None) else {})
    } for _ in chunks]

    with _index_lock:
        delete_article_chunks(str(article.id))
        add_chunks(chunks, metas, ids)


def search_chunks(query: str, mode: Literal["global", "local"]="global", article_id: Optional[str]=None, k: int=4):
    """
    Retrieve relevant chunks.
    - If mode == 'local', apply article_id filter
    - For queries referencing 'latest news', we run a normal similarity_search
      but preferentially sort by metadata['published_at'] if present.
    Returns a list of document-like objects (same shape as earlier).
    """

    # Determine filter
    where = {"article_id": article_id} if mode == "local" and article_id else None

    # Run similarity search
    # Note: some Chromas accept "filter" keyword, others "where"; adapt if needed.
    try:
        if where:
            docs = _vectorstore.similarity_search(query=query, k=k, filter=where)
        else:
            docs = _vectorstore.similarity_search(query=query, k=k)
    except TypeError:
        # fallback if chroma implementation expects 'where' param name
        if where:
            docs = _vectorstore.similarity_search(query=query, k=k, where=where)
        else:
            docs = _vectorstore.similarity_search(query=query, k=k)

    # If the query was 'latest news'-like, prefer sorting by metadata 'published_at' if present
    q_lower = (query or "").lower()
    if any(tok in q_lower for tok in ("latest", "recent", "today")):
        # only sort if metadata published_at exists on some docs
        try:
            docs_with_dates = []
            docs_without_dates = []
            for d in docs:
                m = getattr(d, "metadata", None) or {}
                pub = m.get("published_at")
                if pub:
                    docs_with_dates.append((pub, d))
                else:
                    docs_without_dates.append(d)
            if docs_with_dates:
                # sort descending by published_at (assumes ISO or comparable)
                docs_with_dates.sort(key=lambda x: x[0], reverse=True)
                docs_sorted = [d for _, d in docs_with_dates] + docs_without_dates
                return docs_sorted[:k]
        except Exception:
            # if any error, fall back to original docs
            return docs[:k]

    return docs[:k]
