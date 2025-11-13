from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class LookupResult(BaseModel):
    __tablename__ = "lookup_results"
    __table_args__ = (
        Index("ix_lookup_results_ip_str", "ip_str"),
        Index("ix_lookup_results_ip_provider", "ip_str", "provider_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ip_str: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv4/IPv6 у тексті
    country: Mapped[Optional[str]] = mapped_column(String(2))        # ISO-3166-1 alpha-2
    asn: Mapped[Optional[int]] = mapped_column(Integer)
    org_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_vpn: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_tor: Mapped[Optional[bool]] = mapped_column(Boolean)
    provider_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("providers.id", ondelete="SET NULL"), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)

    provider: Mapped[Optional["Provider"]] = relationship(back_populates="lookup_results")
    queries: Mapped[list["IpQuery"]] = relationship(back_populates="result")
