from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings

GROQ_API_KEY = settings.GROQ_API_KEY
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

# Use same model style you used in chat endpoint
GROQ_MODEL = "llama-3.3-70b-versatile"

# LLM client (consistent with your chat.py style)
llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.2,
)

# Prompt template in LangChain syntax (same pattern as your chat code)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You summarize news articles accurately."),
    ("human",
     "Summarize the following news article in a concise, factual way "
     "without adding opinions or speculation:\n\n{text}"
    )
])


def summarize_news(text: str) -> str:
    """
    Summarize a news article using Groq LLM via LangChain.
    Fully compatible replacement for the previous raw requests version.
    """

    chain = prompt | llm

    try:
        result = chain.invoke({"text": text})
    except Exception as e:
        raise RuntimeError(f"Groq summarization failed: {e}")

    # Extract final answer safely (same pattern as your chat.py extractor)
    if hasattr(result, "content"):
        summary = result.content
    else:
        summary = str(result)

    return summary.strip()
