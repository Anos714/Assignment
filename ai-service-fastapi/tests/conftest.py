import pytest

from app.core.settings import settings


@pytest.fixture(autouse=True)
def use_extractive_llm(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "extractive")
