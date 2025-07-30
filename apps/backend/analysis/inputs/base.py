"""Base input processor and main interface for extensible input handling."""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import mimetypes
from enum import Enum


class InputType(Enum):
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    DIRECTORY = "directory"
    COMPOSITE = "composite"
    UNKNOWN = "unknown"


@dataclass
class ProcessedInput:
    """Standardized output from all input processors"""
    content: str  # Main extracted content
    metadata: Dict[str, Any]  # Additional metadata
    source_type: InputType
    source_path: str
    confidence: float = 1.0  # Confidence in extraction quality
    assumptions: List[str] = None  # Any assumptions made during processing
    
    def __post_init__(self):
        if self.assumptions is None:
            self.assumptions = []


class BaseProcessor(ABC):
    """Abstract base class for all input processors"""
    
    @abstractmethod
    def can_process(self, input_path: Union[str, Path]) -> bool:
        """Check if this processor can handle the given input"""
        pass
    
    @abstractmethod
    def process(self, input_path: Union[str, Path], **kwargs) -> ProcessedInput:
        """Process the input and return standardized output"""
        pass


class InputProcessor:
    """Main interface for extensible input handling"""
    
    def __init__(self):
        # Import here to avoid circular dependencies
        from .text import TextProcessor
        from .image import ImageProcessor
        from .composite import CompositeProcessor
        from .pdf import PDFProcessor
        
        self.processors = {
            InputType.TEXT: TextProcessor(),
            InputType.IMAGE: ImageProcessor(),
            InputType.COMPOSITE: CompositeProcessor()
        }
        
        # Add PDF processor
        self.pdf_processor = PDFProcessor()
    
    def detect_type(self, input_spec: Union[str, Dict[str, Any]]) -> InputType:
        """Detect input type from path or specification"""
        if isinstance(input_spec, dict):
            # Handle complex input specifications
            if 'sources' in input_spec:
                return InputType.COMPOSITE
            input_path = input_spec.get('path', '')
        else:
            input_path = input_spec
        
        path = Path(input_path)
        
        # Check if directory
        if path.is_dir():
            return InputType.DIRECTORY
        
        # Check file type by extension and mimetype
        if path.is_file():
            mime_type, _ = mimetypes.guess_type(str(path))
            ext = path.suffix.lower()
            
            # Image files
            if mime_type and mime_type.startswith('image/'):
                return InputType.IMAGE
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']:
                return InputType.IMAGE
            
            # PDF files
            if mime_type == 'application/pdf' or ext == '.pdf':
                return InputType.TEXT  # PDFs are processed as text
            
            # Text files
            if mime_type and mime_type.startswith('text/'):
                return InputType.TEXT
            if ext in ['.txt', '.md', '.rst', '.log']:
                return InputType.TEXT
            
            # Code files (will be handled by code processor in future)
            if ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.go', '.rs']:
                return InputType.CODE
        
        return InputType.UNKNOWN
    
    def process(self, input_spec: Union[str, Dict[str, Any]], **kwargs) -> ProcessedInput:
        """Process input regardless of type"""
        # Extract path from spec
        if isinstance(input_spec, dict):
            input_path = input_spec.get('path', input_spec)
        else:
            input_path = input_spec
        
        path = Path(input_path)
        
        # Check if it's a PDF first
        if path.suffix.lower() == '.pdf':
            return self.pdf_processor.process(input_path, **kwargs)
        
        input_type = self.detect_type(input_spec)
        
        # For directories, use composite processor
        if input_type == InputType.DIRECTORY:
            input_type = InputType.COMPOSITE
        
        # For code files, fall back to text processor for now
        if input_type == InputType.CODE:
            input_type = InputType.TEXT
        
        if input_type == InputType.UNKNOWN:
            # Try text processor as fallback
            input_type = InputType.TEXT
        
        processor = self.processors.get(input_type)
        if not processor:
            raise ValueError(f"No processor available for input type: {input_type}")
        
        return processor.process(input_path, **kwargs)
    
    def process_multiple(self, inputs: List[Union[str, Dict[str, Any]]], **kwargs) -> List[ProcessedInput]:
        """Process multiple inputs and return combined results"""
        results = []
        for input_spec in inputs:
            try:
                result = self.process(input_spec, **kwargs)
                results.append(result)
            except Exception as e:
                # Log error but continue processing other inputs
                print(f"Error processing {input_spec}: {e}")
        return results