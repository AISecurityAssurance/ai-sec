from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class AnalysisStatus(str, Enum):
    """Analysis status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FrameworkType(str, Enum):
    """Security analysis frameworks"""
    STPA_SEC = "stpa-sec"
    STRIDE = "stride"
    PASTA = "pasta"
    DREAD = "dread"
    MAESTRO = "maestro"
    LINDDUN = "linddun"
    HAZOP = "hazop"
    OCTAVE = "octave"


class Analysis(Base):
    """Main analysis table"""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    system_description = Column(Text, nullable=False)
    
    # Status tracking
    status = Column(String(50), default=AnalysisStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # User info (for future auth)
    user_id = Column(String(255))
    
    # Configuration
    config = Column(JSON, default={})
    selected_frameworks = Column(JSON, default=[])
    
    # Performance metrics
    total_duration = Column(Float)  # seconds
    token_usage = Column(JSON, default={})
    
    # Relationships
    sections = relationship("AnalysisSection", back_populates="analysis", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="analysis", cascade="all, delete-orphan")
    versions = relationship("AnalysisVersion", back_populates="analysis", cascade="all, delete-orphan")


class AnalysisSection(Base):
    """Individual sections of an analysis"""
    __tablename__ = "analysis_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    
    framework = Column(String(50), nullable=False)
    section_id = Column(String(100), nullable=False)  # e.g., "threats", "risks"
    title = Column(String(255), nullable=False)
    
    # Content
    content = Column(JSON, nullable=False)  # Structured content matching frontend templates
    template_type = Column(String(50))  # e.g., "table", "chart", "diagram"
    
    # Status
    status = Column(String(50), default=AnalysisStatus.PENDING)
    error_message = Column(Text)
    
    # User modifications
    is_locked = Column(Boolean, default=False)
    user_modifications = Column(JSON, default={})
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    duration = Column(Float)  # seconds
    
    # Relationships
    analysis = relationship("Analysis", back_populates="sections")


class Artifact(Base):
    """Artifacts generated during analysis"""
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., "diagram", "report", "data"
    format = Column(String(50))  # e.g., "json", "svg", "pdf"
    
    # Content
    content = Column(JSON)
    file_path = Column(String(500))  # For large files stored on disk
    
    # Source tracking
    source_framework = Column(String(50))
    source_section = Column(String(100))
    
    # Metadata
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("Analysis", back_populates="artifacts")


class AnalysisVersion(Base):
    """Version history for analyses"""
    __tablename__ = "analysis_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    
    version_number = Column(Integer, nullable=False)
    description = Column(Text)
    
    # Snapshot of analysis state
    snapshot = Column(JSON, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    
    # Relationships
    analysis = relationship("Analysis", back_populates="versions")


class AnalysisTemplate(Base):
    """Reusable analysis templates"""
    __tablename__ = "analysis_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    
    # Template configuration
    frameworks = Column(JSON, nullable=False)  # List of frameworks to use
    config = Column(JSON, default={})  # Default configuration
    
    # Metadata
    is_public = Column(Boolean, default=False)
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalysisCache(Base):
    """Cache for expensive operations"""
    __tablename__ = "analysis_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(500), nullable=False, unique=True)
    
    # Cached data
    value = Column(JSON, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    hits = Column(Integer, default=0)