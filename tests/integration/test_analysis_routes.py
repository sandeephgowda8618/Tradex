import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models import Base


class FakeAlphaService:
    def __init__(self, api_key: str):
        self.api_key = api_key


class FakeOrchestrator:
    def __init__(self, alpha_service):
        self.alpha_service = alpha_service

    def analyze(self, *args, **kwargs):
        return {
            "fundamental_analysis": {"overall_score": 7.0},
            "technical_analysis": {"overall_technical_score": 6.0},
            "combined_analysis": {"overall_score": 6.6},
        }

    def _build_llm_payload(self, *args, **kwargs):
        return {"symbol": "AAPL", "overall_score": 6.6}


def test_analysis_flow(monkeypatch):
    os.environ["ALPHA_VANTAGE_API_KEY"] = "test"

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr("app.api.routes.analysis.AlphaVantageService", FakeAlphaService)
    monkeypatch.setattr("app.api.routes.analysis.AnalysisOrchestrator", FakeOrchestrator)
    monkeypatch.setattr("app.api.routes.analysis.generate_llm_analysis.delay", lambda *args, **kwargs: None)

    client = TestClient(app)

    response = client.post("/analysis/?symbol=AAPL")
    assert response.status_code == 200
    payload = response.json()
    assert "analysis_id" in payload

    analysis_id = payload["analysis_id"]

    response = client.get(f"/analysis/{analysis_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["combined"] is not None
    assert data["llm_status"] == "pending"

    app.dependency_overrides.clear()
