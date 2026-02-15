from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id"), nullable=False)
    fundamental_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    technical_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    combined_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    llm_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    llm_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_bull_case: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_bear_case: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_risk_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    llm_created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    analysis = relationship("Analysis", back_populates="result")
