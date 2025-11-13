from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    api_tokens: Mapped[list["ApiToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
