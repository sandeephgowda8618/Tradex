import json

from app.services.interpretation_engine import InterpretationEngine


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload
        self.status_code = 200
        self.text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_llm_parsing_success(monkeypatch):
    mock_output = {
        "response": json.dumps(
            {
                "executive_summary": "Test",
                "bull_case": "Test",
                "bear_case": "Test",
                "risk_assessment": "Test",
                "confidence": "Medium",
            }
        )
    }

    def fake_post(*args, **kwargs):
        return FakeResponse(mock_output)

    monkeypatch.setattr("requests.post", fake_post)

    engine = InterpretationEngine()
    result = engine.generate({"symbol": "TEST", "overall_score": 6.5})

    assert "parsed" in result
    assert result["parsed"]["confidence"] == "Medium"


def test_llm_parsing_failure(monkeypatch):
    mock_output = {"response": "not-json"}

    def fake_post(*args, **kwargs):
        return FakeResponse(mock_output)

    monkeypatch.setattr("requests.post", fake_post)

    engine = InterpretationEngine()
    result = engine.generate({"symbol": "TEST", "overall_score": 6.5})

    assert result["parsed"] == {}


def test_llm_fallback_model(monkeypatch):
    calls = {"count": 0}

    class FakeResponse:
        def __init__(self, status_code, payload, text=""):
            self.status_code = status_code
            self._payload = payload
            self.text = text

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("http error")

        def json(self):
            return self._payload

    def fake_post(url, **kwargs):
        _payload = kwargs.get("json")
        calls["count"] += 1
        # first call returns model-not-found 404
        if calls["count"] == 1:
            return FakeResponse(404, {"error": "model not found"}, text="{\"error\":\"model 'x' not found\"}")
        # second call succeeds
        return FakeResponse(
            200,
            {
                "response": json.dumps(
                    {
                        "executive_summary": "OK",
                        "bull_case": "OK",
                        "bear_case": "OK",
                        "risk_assessment": "OK",
                        "confidence": "Low",
                    }
                )
            },
        )

    def fake_get(url, **kwargs):
        return FakeResponse(200, {"models": [{"name": "llama3.1:latest"}]})

    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr("requests.get", fake_get)

    import os
    os.environ["OLLAMA_MODEL"] = "missing-model"
    engine = InterpretationEngine(model="missing-model", base_url="http://127.0.0.1:11434")
    result = engine.generate({"symbol": "TEST", "overall_score": 6.5})

    assert result["parsed"]["executive_summary"] == "OK"
