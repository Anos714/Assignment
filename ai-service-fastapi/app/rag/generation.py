import json
import re
from urllib.request import Request, urlopen

from app.core.settings import settings
from app.rag.embeddings import tokenize
from app.rag.retrieval import RetrievedChunk
from app.schemas import Citation


DEFAULT_REFUSAL = (
    "I could not find enough supporting information in your uploaded documents "
    "to answer this question."
)

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def build_grounded_answer(question: str, retrieved: list[RetrievedChunk]) -> tuple[str, list[Citation]]:
    if not retrieved:
        return DEFAULT_REFUSAL, []

    question_terms = {term for term in tokenize(question) if term not in STOPWORDS}
    selected: list[tuple[RetrievedChunk, str]] = []
    for item in retrieved:
        sentence = _best_sentence(item.chunk.content, question_terms)
        if sentence:
            selected.append((item, sentence))
        if len(selected) >= 3:
            break

    if not selected:
        return DEFAULT_REFUSAL, []

    citations = [
        Citation(
            document_id=item.chunk.document_id,
            document_name=item.chunk.document_name,
            chunk_id=item.chunk.id,
            page_number=item.chunk.page_number,
            score=round(item.score, 4),
            supporting_text=sentence,
        )
        for item, sentence in selected
    ]
    if settings.llm_provider == "openai" and settings.openai_api_key:
        answer = _openai_grounded_answer(question, citations)
    else:
        answer = " ".join(sentence for _, sentence in selected)
    return answer, citations


def _best_sentence(content: str, question_terms: set[str]) -> str:
    candidates = [sentence.strip() for sentence in SENTENCE_RE.split(content) if sentence.strip()]
    if not candidates:
        candidates = [content.strip()]
    scored = sorted(
        candidates,
        key=lambda sentence: (
            len(question_terms.intersection(tokenize(sentence))),
            min(len(sentence), 600),
        ),
        reverse=True,
    )
    return scored[0][:1200].strip()


def _openai_grounded_answer(question: str, citations: list[Citation]) -> str:
    context = "\n\n".join(
        f"[{index + 1}] {citation.document_name}"
        f"{f' page {citation.page_number}' if citation.page_number else ''}: "
        f"{citation.supporting_text}"
        for index, citation in enumerate(citations)
    )
    prompt = (
        "Answer only using the supplied context. "
        "If the context is insufficient, say you could not find enough supporting information. "
        "Keep the answer concise and do not invent facts.\n\n"
        f"Question: {question}\n\nContext:\n{context}"
    )
    request = Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(
            {
                "model": settings.openai_chat_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            }
        ).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"].strip()
