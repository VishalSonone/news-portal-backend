from typing import List, Optional, Literal

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

# embedding fn using plain cohere
def _embed_documents(texts: List[str]) -> List[List[float]]:
    client = cohere.Client(COHERE_API_KEY)
    resp = client.embed(
        texts=texts,
        model=COHERE_EMBED_MODEL,
        input_type="search_document"
    )
    return resp.embeddings

def _embed_query(text: str) -> List[float]:
    client = cohere.Client(COHERE_API_KEY)
    resp = client.embed(
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

# we need manual add using embed_documents instead of embed_query
def add_chunks(texts: List[str], metadatas: List[dict], ids: List[str]):
    vecs = _embed_documents(texts)
    _vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids, embeddings=vecs)


# -------------------------- public helpers --------------------------

def build_document_text(article):
    parts = []
    if article.title:
        parts.append(article.title)
    if article.summary:
        parts.append(article.summary)
    if article.content:
        parts.append(article.content)
    return "\n\n".join(p for p in parts if p)

def delete_article_chunks(article_id: str):
    # remove chunks by metadata filter
    _vectorstore.delete(where={"article_id": article_id})


def index_article(article):
    text = build_document_text(article)
    if not text or not text.strip():
        delete_article_chunks(str(article.id))
        return

    chunks = _splitter.split_text(text)
    delete_article_chunks(str(article.id))

    ids = [f"{article.id}:{i}" for i in range(len(chunks))]
    metas = [{
        "article_id": str(article.id),
        "slug": article.slug,
        "category_id": article.category_id,
        "status": article.status.value if hasattr(article.status, "value") else str(article.status)
    } for _ in chunks]

    add_chunks(chunks, metas, ids)

def search_chunks(query: str, mode: Literal["global", "local"]="global", article_id: Optional[str]=None, k: int=4):
    if mode == "local":
        if not article_id:
            raise ValueError("article_id required in local mode")
        return _vectorstore.similarity_search(query=query, k=k, filter={"article_id": article_id})
    return _vectorstore.similarity_search(query=query, k=k)
