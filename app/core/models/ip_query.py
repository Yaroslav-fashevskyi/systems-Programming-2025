from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class IpQuery(BaseModel):
    __tablename__ = "ip_queries"
    __table_args__ = (
        Index("ix_ip_queries_created_at", "created_at"),
        Index("ix_ip_queries_project_created", "project_id", "created_at"),
        Index("ix_ip_queries_token_created", "token_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    token_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("api_tokens.id", ondelete="SET NULL"), index=True)
    ip_requested: Mapped[str] = mapped_column(String(45), nullable=False)
    result_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("lookup_results.id", ondelete="SET NULL"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="OK", nullable=False)  # OK/ERROR/CACHE
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)

    project: Mapped[Optional["Project"]] = relationship(back_populates="ip_queries")
    token: Mapped[Optional["ApiToken"]] = relationship(back_populates="ip_queries")
    result: Mapped[Optional["LookupResult"]] = relationship(back_populates="queries")
