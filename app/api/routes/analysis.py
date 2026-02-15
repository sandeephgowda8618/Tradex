from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.analysis_result import AnalysisResult
from app.models.thread import Thread
from app.models.user import User
from app.services.alpha_vantage_service import AlphaVantageService
from app.services.analysis_orchestrator import AnalysisOrchestrator
from app.tasks.llm_tasks import generate_llm_analysis
from app.utils.logger import get_logger


router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = get_logger(__name__)


def _get_or_create_system_user(db: Session) -> User:
    user = db.query(User).filter(User.email == "system@local").first()
    if user:
        return user
    user = User(email="system@local", hashed_password="", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _get_or_create_thread(db: Session, thread_id: str | None) -> Thread:
    if thread_id:
        thread = db.query(Thread).filter(Thread.id == thread_id).first()
        if thread:
            return thread
    user = _get_or_create_system_user(db)
    now = datetime.now(UTC)
    thread = Thread(id=str(uuid4()), user_id=user.id, title=None, created_at=now, updated_at=now)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


@router.post("/")
def create_analysis(
    symbol: str,
    selected_fundamentals: list[str] | None = None,
    selected_technicals: list[str] | None = None,
    include_llm: bool = True,
    thread_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    logger.info("POST /analysis | symbol=%s", symbol)
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    if not api_key:
        logger.error("ALPHA_VANTAGE_API_KEY not configured")
        raise HTTPException(status_code=500, detail="ALPHA_VANTAGE_API_KEY not configured")

    try:
        thread = _get_or_create_thread(db, thread_id)
        analysis_id = str(uuid4())

        analysis = Analysis(
            id=analysis_id,
            thread_id=thread.id,
            symbol=symbol.upper(),
            selected_fundamentals=selected_fundamentals,
            selected_technicals=selected_technicals,
            created_at=datetime.now(UTC),
        )
        db.add(analysis)
        db.commit()

        alpha = AlphaVantageService(api_key=api_key)
        orchestrator = AnalysisOrchestrator(alpha_service=alpha)

        result = orchestrator.analyze(
            symbol=symbol,
            selected_fundamentals=selected_fundamentals,
            selected_technicals=selected_technicals,
            include_llm=False,
        )

        analysis_result = AnalysisResult(
            id=str(uuid4()),
            analysis_id=analysis_id,
            fundamental_json=result.get("fundamental_analysis"),
            technical_json=result.get("technical_analysis"),
            combined_json=result.get("combined_analysis"),
            llm_status="pending" if include_llm else None,
        )

        db.add(analysis_result)
        db.commit()

        if include_llm:
            logger.info("Queueing LLM from route | analysis_id=%s", analysis_id)
            llm_payload = orchestrator._build_llm_payload(
                symbol,
                result.get("fundamental_analysis"),
                result.get("technical_analysis"),
                result.get("combined_analysis"),
            )
            generate_llm_analysis.delay(analysis_result.id, llm_payload)
    except Exception:
        logger.exception("POST /analysis failed | symbol=%s", symbol)
        raise

    return {
        "analysis_id": analysis_id,
        "thread_id": thread.id,
        "status": "processing",
    }


@router.get("/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)) -> dict:
    logger.info("GET /analysis/%s", analysis_id)
    result = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.analysis_id == analysis_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "fundamental": result.fundamental_json,
        "technical": result.technical_json,
        "combined": result.combined_json,
        "llm_status": result.llm_status,
        "llm_summary": result.llm_summary,
        "llm_bull_case": result.llm_bull_case,
        "llm_bear_case": result.llm_bear_case,
        "llm_risk_assessment": result.llm_risk_assessment,
        "llm_confidence": result.llm_confidence,
        "llm_ready": result.llm_summary is not None,
    }


@router.get("/")
def get_analysis_by_query(analysis_id: str, db: Session = Depends(get_db)) -> dict:
    logger.info("GET /analysis?analysis_id=%s", analysis_id)
    result = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.analysis_id == analysis_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "fundamental": result.fundamental_json,
        "technical": result.technical_json,
        "combined": result.combined_json,
        "llm_status": result.llm_status,
        "llm_summary": result.llm_summary,
        "llm_bull_case": result.llm_bull_case,
        "llm_bear_case": result.llm_bear_case,
        "llm_risk_assessment": result.llm_risk_assessment,
        "llm_confidence": result.llm_confidence,
        "llm_ready": result.llm_summary is not None,
    }
