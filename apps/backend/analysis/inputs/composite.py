"""Composite input processor for handling multiple files and directories."""

import os
from pathlib import Path
from typing import Union, List, Dict, Any, Set
import fnmatch
from .base import BaseProcessor, ProcessedInput, InputType


class CompositeProcessor(BaseProcessor):
    """Processor for handling multiple inputs, directories, and complex input specifications"""
    
    def __init__(self):
        # Default exclude patterns
        self.default_excludes = {
            # Version control
            '.git', '.svn', '.hg',
            # Build artifacts
            'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build',
            # IDE
            '.idea', '.vscode', '.vs',
            # OS
            '.DS_Store', 'Thumbs.db',
            # Common non-relevant files
            '*.pyc', '*.pyo', '*.log', '*.tmp', '*.temp'
        }
    
    def can_process(self, input_path: Union[str, Path]) -> bool:
        """Composite processor can handle directories and multiple inputs"""
        path = Path(input_path)
        return path.is_dir()
    
    def _should_exclude(self, path: Path, exclude_patterns: Set[str]) -> bool:
        """Check if a path should be excluded based on patterns"""
        path_str = str(path)
        
        for pattern in exclude_patterns:
            # Check against full path
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Check against basename
            if fnmatch.fnmatch(path.name, pattern):
                return True
            # Check if any parent directory matches
            for parent in path.parents:
                if fnmatch.fnmatch(parent.name, pattern):
                    return True
        
        return False
    
    def _collect_files(self, root_path: Path, exclude_patterns: Set[str], 
                      max_files: int = 100) -> List[Path]:
        """Recursively collect relevant files from directory"""
        collected_files = []
        
        for root, dirs, files in os.walk(root_path):
            root_path = Path(root)
            
            # Filter directories to prevent descending into excluded ones
            dirs[:] = [d for d in dirs if not self._should_exclude(root_path / d, exclude_patterns)]
            
            for file in files:
                if len(collected_files) >= max_files:
                    break
                
                file_path = root_path / file
                if not self._should_exclude(file_path, exclude_patterns):
                    collected_files.append(file_path)
        
        return collected_files
    
    def _categorize_files(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Categorize files by their probable content type"""
        categories = {
            'documentation': [],
            'diagrams': [],
            'code': [],
            'config': [],
            'other': []
        }
        
        for file in files:
            ext = file.suffix.lower()
            
            # Documentation
            if ext in ['.md', '.txt', '.rst', '.doc', '.docx', '.pdf']:
                categories['documentation'].append(file)
            # Diagrams
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp']:
                categories['diagrams'].append(file)
            # Code
            elif ext in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts']:
                categories['code'].append(file)
            # Config
            elif ext in ['.yaml', '.yml', '.json', '.xml', '.ini', '.conf']:
                categories['config'].append(file)
            else:
                categories['other'].append(file)
        
        return categories
    
    def process(self, input_path: Union[str, Path, Dict[str, Any]], **kwargs) -> ProcessedInput:
        """Process directory or multiple inputs"""
        # Handle different input specifications
        if isinstance(input_path, dict):
            return self._process_spec(input_path, **kwargs)
        
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input path not found: {path}")
        
        if path.is_file():
            # Single file - delegate to appropriate processor
            from .base import InputProcessor
            processor = InputProcessor()
            return processor.process(str(path), **kwargs)
        
        # Process directory
        exclude_patterns = set(self.default_excludes)
        if 'exclude' in kwargs:
            exclude_patterns.update(kwargs['exclude'])
        
        # Collect files
        files = self._collect_files(path, exclude_patterns, max_files=kwargs.get('max_files', 100))
        
        if not files:
            raise ValueError(f"No processable files found in directory: {path}")
        
        # Categorize files
        categorized = self._categorize_files(files)
        
        # Process files by category
        combined_content = []
        all_assumptions = []
        metadata = {
            'root_directory': str(path),
            'total_files': len(files),
            'categories': {k: len(v) for k, v in categorized.items()},
            'processed_files': []
        }
        
        # Process in priority order
        from .base import InputProcessor
        processor = InputProcessor()
        
        # 1. Documentation first (most likely to have system description)
        for doc_file in categorized['documentation'][:5]:  # Limit to first 5 docs
            try:
                result = processor.process(str(doc_file))
                combined_content.append(f"\n## From {doc_file.name}:\n{result.content}")
                all_assumptions.extend(result.assumptions)
                metadata['processed_files'].append(str(doc_file))
            except:
                pass
        
        # 2. Diagrams (architectural understanding)
        for diagram_file in categorized['diagrams'][:3]:  # Limit to first 3 diagrams
            try:
                result = processor.process(str(diagram_file))
                combined_content.append(f"\n## From diagram {diagram_file.name}:\n{result.content}")
                all_assumptions.extend(result.assumptions)
                metadata['processed_files'].append(str(diagram_file))
            except:
                pass
        
        # 3. Config files (system configuration)
        for config_file in categorized['config'][:5]:
            try:
                result = processor.process(str(config_file))
                combined_content.append(f"\n## Configuration from {config_file.name}:\n{result.content}")
                metadata['processed_files'].append(str(config_file))
            except:
                pass
        
        # Combine all content
        final_content = f"""# System Analysis from Directory: {path.name}

Total files found: {len(files)}
Files processed: {len(metadata['processed_files'])}

{''.join(combined_content)}

## Directory Structure Summary:
- Documentation files: {len(categorized['documentation'])}
- Diagram files: {len(categorized['diagrams'])}
- Code files: {len(categorized['code'])}
- Configuration files: {len(categorized['config'])}
- Other files: {len(categorized['other'])}
"""
        
        # Add assumption about incomplete processing if many files
        if len(files) > len(metadata['processed_files']):
            all_assumptions.append(f"Only {len(metadata['processed_files'])} of {len(files)} files were processed for efficiency")
        
        return ProcessedInput(
            content=final_content,
            metadata=metadata,
            source_type=InputType.COMPOSITE,
            source_path=str(path),
            confidence=0.7,  # Lower confidence due to potential missing context
            assumptions=list(set(all_assumptions))  # Deduplicate
        )
    
    def _process_spec(self, spec: Dict[str, Any], **kwargs) -> ProcessedInput:
        """Process a complex input specification with multiple sources"""
        sources = spec.get('sources', [])
        if not sources:
            raise ValueError("No sources specified in input specification")
        
        from .base import InputProcessor
        processor = InputProcessor()
        
        all_results = []
        combined_content = []
        all_assumptions = []
        metadata = {
            'source_count': len(sources),
            'processed_sources': []
        }
        
        for source in sources:
            try:
                if isinstance(source, str):
                    # Simple path
                    result = processor.process(source, **kwargs)
                else:
                    # Complex source spec
                    source_path = source.get('path')
                    source_kwargs = {**kwargs, **source.get('options', {})}
                    result = processor.process(source_path, **source_kwargs)
                
                all_results.append(result)
                combined_content.append(f"\n## From {result.source_path}:\n{result.content}")
                all_assumptions.extend(result.assumptions)
                metadata['processed_sources'].append(result.source_path)
                
            except Exception as e:
                # Log but continue
                print(f"Error processing source: {e}")
        
        if not all_results:
            raise ValueError("No sources could be processed successfully")
        
        # Combine all content
        final_content = f"""# Combined System Analysis from Multiple Sources

Sources processed: {len(all_results)} of {len(sources)}

{''.join(combined_content)}
"""
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in all_results) / len(all_results)
        
        return ProcessedInput(
            content=final_content,
            metadata=metadata,
            source_type=InputType.COMPOSITE,
            source_path="multiple_sources",
            confidence=avg_confidence,
            assumptions=list(set(all_assumptions))
        )