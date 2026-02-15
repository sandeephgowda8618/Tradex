from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id: Mapped[str] = mapped_column(String(36), ForeignKey("threads.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(12), nullable=False)
    selected_fundamentals: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    selected_technicals: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    thread = relationship("Thread", back_populates="analyses")
    result = relationship("AnalysisResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
