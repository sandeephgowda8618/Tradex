from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.analysis_result import AnalysisResult
from app.services.interpretation_engine import InterpretationEngine
from app.utils.logger import get_logger


@celery_app.task(name="generate_llm_analysis")
def generate_llm_analysis(analysis_result_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    logger = get_logger(__name__)
    logger.info("LLM task started | analysis_result_id=%s", analysis_result_id)
    engine = InterpretationEngine()
    try:
        result = engine.generate(payload)
        status = "completed"
    except Exception:
        logger.exception("LLM task failed | analysis_result_id=%s", analysis_result_id)
        result = {"parsed": {}, "model_used": None}
        status = "failed"

    db = SessionLocal()
    try:
        row = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.id == analysis_result_id)
            .first()
        )

        if row:
            parsed = result.get("parsed", {})
            row.llm_model = result.get("model_used")
            row.llm_status = status
            row.llm_summary = parsed.get("executive_summary")
            row.llm_bull_case = parsed.get("bull_case")
            row.llm_bear_case = parsed.get("bear_case")
            row.llm_risk_assessment = parsed.get("risk_assessment")
            row.llm_confidence = parsed.get("confidence")
            row.llm_created_at = datetime.now(UTC)

            db.commit()
            logger.info("LLM task completed | analysis_result_id=%s", analysis_result_id)
    finally:
        db.close()

    return {"status": status}
