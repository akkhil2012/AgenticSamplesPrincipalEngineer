import asyncio
import json
from dataclasses import replace
import pytest
from src.knowledge.retrieval import KnowledgeService
from src.gateways.model_gateway import ModelGateway
from src.config import Settings
from src.main import create_app
from fastapi.testclient import TestClient


@pytest.mark.parametrize("change", [{"active": False}, {"valid_until": "2000-01-01"}])
def test_stale_inactive_fail_closed(tmp_path, change):
    settings = Settings()
    policies = tmp_path / "policies"
    policies.mkdir()
    for source in (settings.data_dir / "policies").glob("*.json"):
        data = json.loads(source.read_text())
        if data["tenant"] == "bank-a" and data["id"] == "consent":
            data.update(change)
        (policies / source.name).write_text(json.dumps(data))
    service = KnowledgeService(tmp_path)
    with pytest.raises(ValueError):
        service.retrieve("bank-a")
    assert all(p["tenant"] == "bank-b" for p in service.retrieve("bank-b"))


def test_mock_fallback_without_credentials(monkeypatch):
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "AZURE_API_KEY"]:
        monkeypatch.delenv(key, raising=False)
    model = ModelGateway(Settings(model="openai/gpt-4o-mini"))
    result = asyncio.run(model.generate("prepare a campaign", structured=True))
    assert result.fallback and result.model == "mock"
    assert json.loads(result.text) == {"intent": "campaign"}


def test_rate_limit_and_correlation(settings):
    app = create_app(replace(settings, rate_limit=1))
    with TestClient(app) as c:
        first = c.get("/health")
        assert first.status_code == 200 and first.headers["X-Correlation-ID"]
        assert c.get("/health").status_code == 429


def test_latest_inactive_policy_cannot_downgrade(tmp_path):
    import shutil

    shutil.copytree(Settings().data_dir / "policies", tmp_path / "policies")
    path = tmp_path / "policies/bank-a-consent.json"
    newer = {**json.loads(path.read_text()), "version": 2, "active": False}
    (tmp_path / "policies/bank-a-consent-v2.json").write_text(json.dumps(newer))
    with pytest.raises(ValueError):
        KnowledgeService(tmp_path).retrieve("bank-a")


def test_provider_timeout_retries_and_invalid_schema_fallback(monkeypatch):
    import litellm

    calls = []
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")

    async def slow(**kwargs):
        calls.append(True)
        await asyncio.sleep(0.02)

    monkeypatch.setattr(litellm, "acompletion", slow)
    settings = Settings(model="openai/test", model_timeout=0.001, model_retries=1)
    result = asyncio.run(ModelGateway(settings).generate("prepare campaign", structured=True))
    assert len(calls) == 2 and result.fallback
    from types import SimpleNamespace

    async def invalid(**kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"intent":"activate"}'))]
        )

    monkeypatch.setattr(litellm, "acompletion", invalid)
    assert asyncio.run(ModelGateway(settings).generate("prepare campaign", structured=True)).fallback
