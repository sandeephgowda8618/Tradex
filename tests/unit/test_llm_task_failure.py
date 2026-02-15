from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.analysis_result import AnalysisResult
from app.tasks import llm_tasks


def test_llm_task_failure_sets_status(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def fake_generate(_payload):
        raise RuntimeError("LLM failed")

    monkeypatch.setattr(llm_tasks, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(llm_tasks.InterpretationEngine, "generate", staticmethod(fake_generate))

    db = TestingSessionLocal()
    try:
        row = AnalysisResult(
            id="result-2",
            analysis_id="analysis-2",
            created_at=datetime.now(UTC),
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

    result = llm_tasks.generate_llm_analysis("result-2", {"symbol": "TEST"})
    assert result["status"] == "failed"

    db = TestingSessionLocal()
    try:
        updated = db.query(AnalysisResult).filter(AnalysisResult.id == "result-2").first()
        assert updated.llm_status == "failed"
        assert updated.llm_summary is None
    finally:
        db.close()
