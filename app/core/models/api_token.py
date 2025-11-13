from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class ApiToken(BaseModel):
    __tablename__ = "api_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # зберігаємо тільки хеш
    name: Mapped[Optional[str]] = mapped_column(String(120))
    rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="api_tokens")
    project: Mapped[Optional["Project"]] = relationship(back_populates="api_tokens")
    ip_queries: Mapped[list["IpQuery"]] = relationship(back_populates="token")
