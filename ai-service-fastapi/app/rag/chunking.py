from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SourcePage:
    page_number: int | None
    text: str


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    page_number: int | None
    content: str
    metadata: dict


TOKEN_RE = re.compile(r"\S+")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_pages(
    pages: list[SourcePage],
    *,
    chunk_size: int,
    overlap: int,
    filename: str,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    chunk_index = 0
    for page in pages:
        text = normalize_text(page.text)
        if not text:
            continue
        tokens = [match.group(0) for match in TOKEN_RE.finditer(text)]
        start = 0
        while start < len(tokens):
            window = tokens[start : start + chunk_size]
            content = " ".join(window)
            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    content=content,
                    metadata={
                        "source_filename": filename,
                        "token_count": len(window),
                    },
                )
            )
            chunk_index += 1
            if start + chunk_size >= len(tokens):
                break
            start += chunk_size - overlap
    return chunks

