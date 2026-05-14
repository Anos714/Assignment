import hashlib
import json
from uuid import UUID

from redis import Redis
from redis.exceptions import RedisError

from app.core.settings import settings


class Cache:
    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.redis_url
        self.client = Redis.from_url(self.redis_url, decode_responses=True) if self.redis_url else None

    def get_json(self, key: str) -> dict | None:
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (RedisError, json.JSONDecodeError):
            return None

    def set_json(self, key: str, value: dict, ttl_seconds: int) -> None:
        if not self.client:
            return
        try:
            self.client.setex(key, ttl_seconds, json.dumps(value, default=str))
        except RedisError:
            return


def retrieval_cache_key(*, user_id: UUID, question: str, document_ids: list[UUID]) -> str:
    question_hash = hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()[:24]
    scope = ",".join(sorted(str(document_id) for document_id in document_ids)) or "all"
    scope_hash = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:24]
    return f"retrieval:{user_id}:{question_hash}:{scope_hash}"
