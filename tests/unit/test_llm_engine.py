import json

from app.services.interpretation_engine import InterpretationEngine


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

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
