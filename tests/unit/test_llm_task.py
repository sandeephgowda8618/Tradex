from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.analysis_result import AnalysisResult
from app.tasks import llm_tasks


def test_llm_task_updates_db(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def fake_generate(_payload):
        return {
            "model_used": "test-model",
            "parsed": {
                "executive_summary": "Summary",
                "bull_case": "Bull",
                "bear_case": "Bear",
                "risk_assessment": "Risk",
                "confidence": "Medium",
            },
        }

    monkeypatch.setattr(llm_tasks, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(llm_tasks.InterpretationEngine, "generate", staticmethod(fake_generate))

    db = TestingSessionLocal()
    try:
        row = AnalysisResult(
            id="result-1",
            analysis_id="analysis-1",
            created_at=datetime.now(UTC),
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

    result = llm_tasks.generate_llm_analysis("result-1", {"symbol": "TEST"})
    assert result["status"] == "completed"

    db = TestingSessionLocal()
    try:
        updated = db.query(AnalysisResult).filter(AnalysisResult.id == "result-1").first()
        assert updated.llm_summary == "Summary"
        assert updated.llm_confidence == "Medium"
    finally:
        db.close()
