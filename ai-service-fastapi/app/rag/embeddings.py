from collections.abc import Iterable
import json
import hashlib
import math
import re
from urllib.request import Request, urlopen

from app.core.settings import settings

TERM_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TERM_RE.findall(text)]


def embed_text(text: str, dimensions: int) -> list[float]:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return normalize(_openai_embedding(text))
    return hash_embed_text(text, dimensions)


def hash_embed_text(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    return normalize(vector)


def normalize(vector: Iterable[float]) -> list[float]:
    values = [float(value) for value in vector]
    magnitude = math.sqrt(sum(value * value for value in values))
    if magnitude == 0:
        return values
    return [value / magnitude for value in values]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    return sum(left[index] * right[index] for index in range(size))


def _openai_embedding(text: str) -> list[float]:
    request = Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps({"model": settings.openai_embedding_model, "input": text}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [float(value) for value in payload["data"][0]["embedding"]]
