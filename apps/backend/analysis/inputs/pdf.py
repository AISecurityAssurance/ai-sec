"""PDF input processor for handling PDF documents."""

from pathlib import Path
from typing import Union, Optional
from .base import BaseProcessor, ProcessedInput, InputType

# Try to import PyMuPDF, fall back to basic implementation if not available
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    import subprocess


class PDFProcessor(BaseProcessor):
    """Processor for PDF inputs"""
    
    def can_process(self, input_path: Union[str, Path]) -> bool:
        """Check if this processor can handle the given input"""
        path = Path(input_path)
        if not path.is_file():
            return False
        
        return path.suffix.lower() == '.pdf'
    
    def process(self, input_path: Union[str, Path], **kwargs) -> ProcessedInput:
        """Process PDF input and return standardized output"""
        path = Path(input_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        
        if HAS_PYMUPDF:
            return self._process_with_pymupdf(path)
        else:
            return self._process_with_fallback(path)
    
    def _process_with_pymupdf(self, path: Path) -> ProcessedInput:
        """Process PDF using PyMuPDF library"""
        try:
            # Open PDF
            doc = fitz.open(str(path))
            
            # Extract text from all pages
            text_content = []
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():  # Only add non-empty pages
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            
            # Combine all text
            full_text = "\n\n".join(text_content)
            
            # Extract metadata
            metadata = {
                'filename': path.name,
                'file_size': path.stat().st_size,
                'page_count': page_count,
                'pdf_metadata': doc.metadata,
                'word_count': len(full_text.split()),
                'extraction_method': 'PyMuPDF text extraction'
            }
            
            doc.close()
            
            return self._create_processed_input(path, full_text, metadata)
            
        except Exception as e:
            raise ValueError(f"Error processing PDF file {path}: {str(e)}")
    
    def _process_with_fallback(self, path: Path) -> ProcessedInput:
        """Fallback PDF processing using system tools or mock content"""
        try:
            # Try using pdftotext command (commonly available on Linux/Mac)
            result = subprocess.run(
                ['pdftotext', str(path), '-'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                full_text = result.stdout
                metadata = {
                    'filename': path.name,
                    'file_size': path.stat().st_size,
                    'word_count': len(full_text.split()),
                    'extraction_method': 'pdftotext command',
                    'extraction_warning': 'Using fallback extraction - install PyMuPDF for better results'
                }
                return self._create_processed_input(path, full_text, metadata)
            else:
                # If pdftotext fails, provide an error with instructions
                raise ValueError(
                    f"PDF processing failed. Please install PyMuPDF (pip install PyMuPDF) "
                    f"or ensure pdftotext is available. Error: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            raise ValueError(f"PDF processing timed out for {path}")
        except FileNotFoundError:
            # Use mock content for development/testing
            import os
            if os.getenv('USE_MOCK_PDF', 'false').lower() == 'true':
                from .pdf_mock import get_mock_pdf_content
                full_text = get_mock_pdf_content(path.name)
                metadata = {
                    'filename': path.name,
                    'file_size': path.stat().st_size,
                    'word_count': len(full_text.split()),
                    'extraction_method': 'MOCK CONTENT - Development only',
                    'extraction_warning': 'Using mock content - PDF libraries not available'
                }
                return self._create_processed_input(path, full_text, metadata)
            else:
                raise ValueError(
                    "PDF processing not available. Please install PyMuPDF (pip install PyMuPDF) "
                    "or pdftotext (part of poppler-utils). For development, set USE_MOCK_PDF=true"
                )
    
    def _create_processed_input(self, path: Path, full_text: str, metadata: dict) -> ProcessedInput:
        """Create ProcessedInput from extracted text and metadata"""
        # Analyze content
        assumptions = []
        confidence = 0.8  # Base confidence for PDF extraction
        
        content_lower = full_text.lower()
        system_keywords = ['system', 'architecture', 'deployment', 'security', 
                         'network', 'component', 'infrastructure', 'design']
        keyword_count = sum(1 for keyword in system_keywords if keyword in content_lower)
        
        if keyword_count > 10:
            assumptions.append("Document appears to be a technical architecture or design document")
            confidence = 0.9
        elif keyword_count < 3:
            assumptions.append("Document may not be a system description")
            confidence = 0.5
        
        # Check for specific document types
        if 'deployment' in path.name.lower() or 'architecture' in path.name.lower():
            assumptions.append("Filename suggests this is an architecture/deployment document")
            confidence = min(confidence + 0.1, 1.0)
        
        # Handle empty or low-content PDFs
        if len(full_text.strip()) < 100:
            assumptions.append("PDF contains very little text - may be primarily images")
            confidence = 0.3
        
        return ProcessedInput(
            content=full_text,
            metadata=metadata,
            source_type=InputType.TEXT,  # PDFs are processed as text
            source_path=str(path),
            confidence=confidence,
            assumptions=assumptions if assumptions else None
        )