"""Text input processor for handling text-based system descriptions."""

from pathlib import Path
from typing import Union
from .base import BaseProcessor, ProcessedInput, InputType


class TextProcessor(BaseProcessor):
    """Processor for text-based inputs (txt, md, etc.)"""
    
    def can_process(self, input_path: Union[str, Path]) -> bool:
        """Check if this processor can handle the given input"""
        path = Path(input_path)
        if not path.is_file():
            return False
        
        # Check common text extensions
        text_extensions = {'.txt', '.md', '.rst', '.log', '.text', '.markdown'}
        return path.suffix.lower() in text_extensions
    
    def process(self, input_path: Union[str, Path], **kwargs) -> ProcessedInput:
        """Process text input and return standardized output"""
        path = Path(input_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        
        try:
            # Read the text content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to determine what kind of text this is
            content_lower = content.lower()
            assumptions = []
            confidence = 1.0
            
            # Check if this looks like a system description
            system_keywords = ['system', 'architecture', 'component', 'interface', 'data flow', 
                             'security', 'api', 'database', 'server', 'client', 'network']
            system_keyword_count = sum(1 for keyword in system_keywords if keyword in content_lower)
            
            # Check if this might be something else
            if 'recipe' in content_lower or 'ingredients' in content_lower:
                assumptions.append("Content appears to be a recipe, not a system description")
                confidence = 0.1
            elif 'chapter' in content_lower or 'novel' in content_lower:
                assumptions.append("Content appears to be literature, not a system description")
                confidence = 0.1
            elif system_keyword_count < 3 and len(content) < 200:
                assumptions.append("Content may not be a complete system description")
                confidence = 0.5
            elif system_keyword_count > 5:
                assumptions.append("Content appears to be a technical system description")
                confidence = 0.9
            
            # Extract metadata
            metadata = {
                'filename': path.name,
                'file_size': path.stat().st_size,
                'line_count': content.count('\n') + 1,
                'word_count': len(content.split()),
                'encoding': 'utf-8',
                'system_keyword_count': system_keyword_count
            }
            
            return ProcessedInput(
                content=content,
                metadata=metadata,
                source_type=InputType.TEXT,
                source_path=str(path),
                confidence=confidence,
                assumptions=assumptions if assumptions else None
            )
            
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'ascii']:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    metadata = {
                        'filename': path.name,
                        'file_size': path.stat().st_size,
                        'line_count': content.count('\n') + 1,
                        'word_count': len(content.split()),
                        'encoding': encoding,
                        'encoding_warning': f'File was decoded using {encoding} encoding'
                    }
                    
                    return ProcessedInput(
                        content=content,
                        metadata=metadata,
                        source_type=InputType.TEXT,
                        source_path=str(path),
                        confidence=0.9,  # Slightly lower confidence due to encoding issues
                        assumptions=[f"File encoding assumed to be {encoding}"]
                    )
                except:
                    continue
            
            raise ValueError(f"Unable to decode text file: {path}")
        except Exception as e:
            raise ValueError(f"Error processing text file {path}: {str(e)}")