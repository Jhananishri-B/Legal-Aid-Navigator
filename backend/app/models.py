"""
SQLAlchemy ORM models for Legal Aid Navigator.

Tables
------
users              – registered accounts
legal_aid_requests – one per form submission
workflow_stages    – six per request (one row per stage)
workflow_subtasks  – sub-tasks inside each stage
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    String, Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id          = Column(String(36),  primary_key=True, default=_uuid)
    username    = Column(String(100), unique=True, nullable=False, index=True)
    email       = Column(String(255), unique=True, nullable=False, index=True)
    full_name   = Column(String(200), nullable=True)
    hashed_pw   = Column(String(255), nullable=False)
    created_at  = Column(DateTime,    default=datetime.utcnow)

    requests    = relationship("LegalAidRequest", back_populates="user")


# ── Legal Aid Request ─────────────────────────────────────────────────────────

class LegalAidRequest(Base):
    __tablename__ = "legal_aid_requests"

    id           = Column(String(36),  primary_key=True, default=_uuid)
    request_id   = Column(String(20),  unique=True, nullable=False, index=True)  # e.g. LA-2025-00001
    user_id      = Column(String(36),  ForeignKey("users.id"), nullable=False)

    # Overall status
    status        = Column(String(30), default="in_progress")   # in_progress | completed | failed | awaiting_approval
    current_stage = Column(Integer,    default=1)               # 1-6

    # Form data – Location
    country       = Column(String(100), nullable=True)
    state         = Column(String(100), nullable=True)
    district      = Column(String(100), nullable=True)
    city          = Column(String(150), nullable=True)
    pin_code      = Column(String(20),  nullable=True)

    # Form data – Legal Issue
    issue_type               = Column(String(150), nullable=True)
    issue_description        = Column(Text,        nullable=True)
    court_case_in_progress   = Column(String(20),  nullable=True)
    court_deadline           = Column(String(50),  nullable=True)
    urgency                  = Column(String(20),  nullable=True)

    # Form data – Eligibility
    eligibility_category  = Column(String(150), nullable=True)
    eligibility_details   = Column(Text,        nullable=True)
    supporting_document   = Column(String(20),  nullable=True)

    # Form data – Contact
    full_name          = Column(String(200), nullable=True)
    mobile_number      = Column(String(20),  nullable=True)
    email              = Column(String(255), nullable=True)
    preferred_contact  = Column(String(20),  nullable=True)
    consultation_mode  = Column(String(20),  nullable=True)

    # Form data – Appointment
    preferred_date      = Column(String(30),  nullable=True)
    preferred_time_slot = Column(String(50),  nullable=True)
    appt_mode           = Column(String(20),  nullable=True)
    alt_date            = Column(String(30),  nullable=True)
    alt_time_slot       = Column(String(50),  nullable=True)
    additional_notes    = Column(Text,        nullable=True)

    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user    = relationship("User", back_populates="requests")
    stages  = relationship("WorkflowStage", back_populates="request", order_by="WorkflowStage.stage_number", cascade="all, delete-orphan")


# ── Workflow Stage ─────────────────────────────────────────────────────────────

class WorkflowStage(Base):
    __tablename__ = "workflow_stages"

    id            = Column(String(36), primary_key=True, default=_uuid)
    request_id    = Column(String(36), ForeignKey("legal_aid_requests.id"), nullable=False)
    stage_number  = Column(Integer,    nullable=False)   # 1-6
    name          = Column(String(100),nullable=False)
    status        = Column(String(30), default="pending") # pending | in_progress | completed | failed | awaiting_approval
    started_at    = Column(DateTime,   nullable=True)
    completed_at  = Column(DateTime,   nullable=True)
    error         = Column(Text,       nullable=True)
    result_json   = Column(Text,       nullable=True)  # JSON string

    request   = relationship("LegalAidRequest", back_populates="stages")
    subtasks  = relationship("WorkflowSubtask", back_populates="stage", order_by="WorkflowSubtask.order", cascade="all, delete-orphan")


# ── Workflow Subtask ───────────────────────────────────────────────────────────

class WorkflowSubtask(Base):
    __tablename__ = "workflow_subtasks"

    id            = Column(String(36),  primary_key=True, default=_uuid)
    stage_id      = Column(String(36),  ForeignKey("workflow_stages.id"), nullable=False)
    order         = Column(Integer,     default=0)
    label         = Column(String(255), nullable=False)
    description   = Column(String(500), nullable=True)
    status        = Column(String(30),  default="pending")  # pending | in_progress | completed | failed
    completed_at  = Column(DateTime,    nullable=True)
    error         = Column(Text,        nullable=True)

    stage = relationship("WorkflowStage", back_populates="subtasks")
