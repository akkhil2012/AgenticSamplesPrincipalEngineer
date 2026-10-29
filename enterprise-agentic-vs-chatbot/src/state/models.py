from datetime import datetime, timezone
from sqlalchemy import JSON, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Workflow(Base):
    __tablename__ = "workflows"
    __table_args__ = (UniqueConstraint("tenant", "requester", "idempotency_key"),)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant: Mapped[str] = mapped_column(String)
    requester: Mapped[str] = mapped_column(String)
    idempotency_key: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    correlation_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="CREATED")
    checkpoint: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    payload_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    approval: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    outcome: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[str] = mapped_column(String, index=True)
    tenant: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    actor: Mapped[str] = mapped_column(String)
    agent: Mapped[str] = mapped_column(String)
    tool: Mapped[str] = mapped_column(String)
    decision: Mapped[str] = mapped_column(String)
    outcome: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSON, default=dict)


class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String, unique=True)
    tenant: Mapped[str] = mapped_column(String)
    payload_hash: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
