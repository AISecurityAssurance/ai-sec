"""
SQLAlchemy database models
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column, String, DateTime, Boolean, JSON, Text, 
    ForeignKey, Integer, Float, Enum as SQLEnum, 
    UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base
from core.models.schemas import FrameworkType, AnalysisStatus


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_project_owner", "owner_id"),
    )


class Analysis(Base):
    """Analysis model"""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    system_description = Column(Text, nullable=False)
    frameworks = Column(JSON, nullable=False)  # List of FrameworkType values
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="analyses")
    results = relationship("AnalysisResult", back_populates="analysis", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="analysis")
    artifacts = relationship("Artifact", back_populates="analysis", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_analysis_project", "project_id"),
        Index("idx_analysis_status", "status"),
    )


class AnalysisResult(Base):
    """Analysis result for a specific framework"""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    framework = Column(SQLEnum(FrameworkType), nullable=False)
    sections = Column(JSON, nullable=False)  # List of section results
    artifacts = Column(JSON, default=list)  # List of generated artifacts
    duration = Column(Float, nullable=True)  # Duration in seconds
    token_usage = Column(JSON, nullable=True)  # Token usage stats
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("Analysis", back_populates="results")
    
    __table_args__ = (
        UniqueConstraint("analysis_id", "framework", name="uq_analysis_framework"),
        Index("idx_result_analysis", "analysis_id"),
    )


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)  # Model info, tokens used, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
    analysis = relationship("Analysis", back_populates="chat_messages")
    
    __table_args__ = (
        Index("idx_chat_user", "user_id"),
        Index("idx_chat_analysis", "analysis_id"),
        Index("idx_chat_created", "created_at"),
    )


class Artifact(Base):
    """Analysis artifact model"""
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    framework = Column(SQLEnum(FrameworkType), nullable=False)
    artifact_type = Column(String(100), nullable=False)  # e.g., "hazards", "threats", "controls"
    name = Column(String(255), nullable=False)
    data = Column(JSON, nullable=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("Analysis", back_populates="artifacts")
    
    __table_args__ = (
        Index("idx_artifact_analysis", "analysis_id"),
        Index("idx_artifact_type", "artifact_type"),
        Index("idx_artifact_framework", "framework"),
    )


class SystemComponent(Base):
    """System component for graph database sync"""
    __tablename__ = "system_components"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    component_type = Column(String(100), nullable=False)  # controller, process, sensor, etc.
    name = Column(String(255), nullable=False)
    properties = Column(JSON, default=dict)
    neo4j_id = Column(String(100), nullable=True)  # Neo4j node ID for sync
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_component_analysis", "analysis_id"),
        Index("idx_component_type", "component_type"),
        UniqueConstraint("analysis_id", "name", name="uq_analysis_component"),
    )