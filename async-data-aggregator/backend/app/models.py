"""SQLAlchemy models."""

import enum

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func

from app.database import Base


class JobStatus(str, enum.Enum):
    """Status of an aggregation job."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AggregationJob(Base):
    """Model for aggregation jobs."""

    __tablename__ = "aggregation_jobs"

    id = Column(String(36), primary_key=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    sources = Column(ARRAY(String), nullable=False)
    parameters = Column(JSONB, nullable=False, default=dict)
    result_url = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
