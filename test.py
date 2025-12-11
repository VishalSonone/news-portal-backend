# test_embedding_debug.py
import traceback
from datetime import datetime

from app.services.embedding_service import (
    index_article,
    search_chunks,
    build_document_text,
)

# simple stub article-like object
class DummyArticle:
    def __init__(self, id, title, summary, content, slug="test-slug", category_id=1, status="published"):
        self.id = id
        self.title = title
        self.summary = summary
        self.content = content
        self.slug = slug
        self.category_id = category_id
        self.status = status

def log(msg):
    with open("embedding_debug.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow()}] {msg}\n")

def main():
    try:
        log("=== TEST START ===")
        article = DummyArticle(
            id="debug-123",
            title="Debug Title",
            summary="Debug summary",
            content="Debug content about AI and news portal."
        )

        log("Indexing article...")
        index_article(article)
        log("Index done")

        log("Searching...")
        docs = search_chunks(
            query="news portal",
            mode="global",
            article_id=None,
            k=4
        )
        log(f"Search returned {len(docs)} docs")
        for d in docs:
            log(f"doc snippet={d.page_content[:60]}")

    except Exception as e:
        log("ERROR: " + str(e))
        log(traceback.format_exc())
    finally:
        log("=== TEST END ===\n\n")

if __name__ == "__main__":
    main()
