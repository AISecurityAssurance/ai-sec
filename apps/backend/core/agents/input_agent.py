"""
Input Agent for centralized input management and analysis
Handles classification, extraction, and indexing of all input types
"""
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from uuid import uuid4
import asyncio

from core.agents.base import BaseAnalysisAgent
from analysis.inputs import InputProcessor
from core.utils.json_parser import parse_llm_json

logger = logging.getLogger(__name__)


class InputAnalysisResult:
    """Result from input analysis
    
    Attributes:
        confidence: Currently disabled. When implemented, should represent:
                   - For classification: P(correct classification | features)
                   - For extraction: Completeness of extracted information (0-1)
                   - Should be based on actual validation, not arbitrary values
    """
    def __init__(self, input_id: str, source_path: str, input_type: str, 
                 summary: str, content: Any, metadata: Dict[str, Any],
                 confidence: Optional[float] = None):
        self.input_id = input_id
        self.source_path = source_path
        self.input_type = input_type
        self.summary = summary
        self.content = content
        self.metadata = metadata
        self.confidence = confidence
        self.timestamp = datetime.now()
        self.extraction_errors = []


class InputAgent:
    """
    Centralized agent for managing all inputs throughout the analysis process
    
    Responsibilities:
    - Classify input types (diagram, text, code, etc.)
    - Extract relevant information
    - Index content for querying
    - Provide summaries and metadata
    - Handle multi-file inputs (PDFs, directories, etc.)
    """
    
    def __init__(self, analysis_id: str, db_connection=None):
        self.analysis_id = analysis_id
        self.db_connection = db_connection
        self.inputs: Dict[str, InputAnalysisResult] = {}
        self.input_processor = InputProcessor()
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{analysis_id[:8]}")
        
    async def process_inputs(self, input_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple inputs and build indexed knowledge base
        
        Args:
            input_configs: List of input configurations (path, type, etc.)
            
        Returns:
            Summary of processed inputs with metadata
        """
        self.logger.info(f"Processing {len(input_configs)} inputs")
        
        results = []
        for config in input_configs:
            try:
                result = await self.analyze_input(config)
                self.inputs[result.input_id] = result
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process input {config}: {e}")
                # Create error result
                error_result = InputAnalysisResult(
                    input_id=str(uuid4()),
                    source_path=config.get('path', 'unknown'),
                    input_type='error',
                    summary=f"Failed to process: {str(e)}",
                    content=None,
                    metadata={'error': str(e)},
                    confidence=None
                )
                error_result.extraction_errors.append(str(e))
                results.append(error_result)
        
        # Generate summary
        summary = self._generate_input_summary(results)
        
        # Store in database if available
        if self.db_connection:
            await self._store_analysis_results(summary)
        
        return summary
    
    async def analyze_input(self, input_config: Dict[str, Any]) -> InputAnalysisResult:
        """
        Analyze a single input to determine type, quality, and content
        
        Args:
            input_config: Input configuration (path, type hints, etc.)
            
        Returns:
            Analysis result with classification and extracted info
        """
        path = input_config.get('path')
        self.logger.info(f"Analyzing input: {path}")
        
        # Process using input processor
        try:
            processed = self.input_processor.process(path)
        except Exception as e:
            self.logger.error(f"Input processor failed for {path}: {e}")
            raise
        
        # Classify and summarize based on content
        classification = await self._classify_input(processed)
        summary = await self._generate_summary(processed, classification)
        
        # Extract structured information based on type
        extracted_info = await self._extract_information(processed, classification)
        
        # Determine display type based on actual file format
        display_type = classification['type']
        metadata = processed.metadata or {}
        if metadata.get('extraction_method') and 'PDF' in metadata.get('extraction_method', ''):
            display_type = 'PDF Document'
        elif metadata.get('filename', '').lower().endswith('.pdf'):
            display_type = 'PDF Document'
        elif display_type == 'general_text':
            display_type = 'Text Document'
        else:
            # Capitalize and format nicely
            display_type = display_type.replace('_', ' ').title()
        
        # Create result
        result = InputAnalysisResult(
            input_id=str(uuid4()),
            source_path=path,
            input_type=display_type,
            summary=summary,
            content=processed.content,
            metadata={
                'original_metadata': processed.metadata,
                'classification': classification,
                'extracted_info': extracted_info,
                'processing_confidence': processed.confidence,
                'assumptions': processed.assumptions
            },
            confidence=classification.get('confidence')  # Will be None for now
        )
        
        return result
    
    async def _classify_input(self, processed_input) -> Dict[str, Any]:
        """
        Classify the input type and determine its relevance
        
        Returns classification with:
        - type: specific content type (system_description, architecture_diagram, etc.)
        - category: general category (documentation, diagram, code, etc.)  
        - relevance: how relevant to security analysis
        - confidence: classification confidence
        """
        content_preview = processed_input.content[:1000] if processed_input.content else ""
        
        # For now, use heuristics. In future, could use LLM
        # Note: Confidence is currently not meaningful - just indicates
        # whether we have high/medium/low certainty about the classification
        classification = {
            'category': processed_input.source_type.value,
            'confidence': None  # Disabled until we have meaningful metrics
        }
        
        # Specific classification based on content
        if processed_input.source_type.value == 'text':
            # Check content for system-related keywords
            system_keywords = ['system', 'architecture', 'component', 'service', 'api', 'database']
            keyword_count = sum(1 for kw in system_keywords if kw.lower() in content_preview.lower())
            
            if keyword_count > 3:
                classification['type'] = 'system_description'
                classification['relevance'] = 'high'
            elif 'requirement' in content_preview.lower():
                classification['type'] = 'requirements_document'
                classification['relevance'] = 'high'
            else:
                classification['type'] = 'general_text'
                classification['relevance'] = 'medium'
                
        elif processed_input.source_type.value == 'image':
            # Check filename for clues
            filename = processed_input.metadata.get('filename', '').lower()
            if any(term in filename for term in ['arch', 'diagram', 'topology', 'flow']):
                classification['type'] = 'architecture_diagram'
                classification['relevance'] = 'high'
            else:
                classification['type'] = 'general_image'
                classification['relevance'] = 'low'
        
        return classification
    
    async def _generate_summary(self, processed_input, classification: Dict[str, Any]) -> str:
        """Generate a one-line summary of the input"""
        input_type = classification.get('type', 'unknown')
        filename = processed_input.metadata.get('filename', 'unnamed')
        
        # Check if this is a PDF
        metadata = processed_input.metadata or {}
        extraction_method = metadata.get('extraction_method', '')
        
        # Create format prefix
        format_prefix = ""
        if 'PDF' in extraction_method or filename.lower().endswith('.pdf'):
            page_count = metadata.get('page_count', 0)
            if page_count > 1:
                format_prefix = f"Multi-page PDF ({page_count} pages) - "
            else:
                format_prefix = "PDF document - "
        
        # Type-specific summaries
        if input_type == 'system_description':
            return f"{format_prefix}System description document detailing architecture and components"
        elif input_type == 'architecture_diagram':
            return f"{format_prefix}Architecture diagram showing system structure and relationships"
        elif input_type == 'requirements_document':
            return f"{format_prefix}Requirements document specifying system constraints and needs"
        else:
            return f"{format_prefix}{input_type.replace('_', ' ').title()} file for analysis"
    
    async def _extract_information(self, processed_input, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured information based on input type
        
        This is where we'd extract:
        - Components from diagrams
        - Requirements from documents
        - APIs from code
        - etc.
        """
        extracted = {
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_method': 'heuristic'  # or 'llm' when we add that
        }
        
        # For now, just note what we would extract
        input_type = classification.get('type', 'unknown')
        
        if input_type == 'architecture_diagram':
            extracted['potential_extractions'] = [
                'system_components',
                'component_connections', 
                'external_interfaces',
                'security_boundaries'
            ]
        elif input_type == 'system_description':
            extracted['potential_extractions'] = [
                'system_purpose',
                'key_features',
                'stakeholders',
                'constraints'
            ]
        
        return extracted
    
    def _generate_input_summary(self, results: List[InputAnalysisResult]) -> Dict[str, Any]:
        """Generate overall summary of all inputs"""
        summary = {
            'total_inputs': len(results),
            'inputs_by_type': {},
            'inputs_by_relevance': {'high': 0, 'medium': 0, 'low': 0},
            'processing_errors': [],
            'input_registry': []
        }
        
        for result in results:
            # Count by type
            input_type = result.input_type
            summary['inputs_by_type'][input_type] = summary['inputs_by_type'].get(input_type, 0) + 1
            
            # Count by relevance
            relevance = result.metadata.get('classification', {}).get('relevance', 'medium')
            summary['inputs_by_relevance'][relevance] += 1
            
            # Track errors
            if result.extraction_errors:
                summary['processing_errors'].extend(result.extraction_errors)
            
            # Build registry entry
            registry_entry = {
                'input_id': result.input_id,
                'filename': Path(result.source_path).name,
                'path': result.source_path,
                'type': result.input_type,
                'summary': result.summary,
                'relevance': relevance
            }
            summary['input_registry'].append(registry_entry)
        
        return summary
    
    async def _store_analysis_results(self, summary: Dict[str, Any]):
        """Store input analysis results in database"""
        if not self.db_connection:
            return
            
        try:
            # Store each input result individually
            for input_entry in summary.get('input_registry', []):
                await self.db_connection.execute("""
                    INSERT INTO input_analysis 
                    (analysis_id, input_name, input_type, input_path, summary, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                    self.analysis_id, 
                    input_entry['filename'],
                    input_entry['type'],
                    input_entry.get('path', input_entry['filename']),
                    input_entry['summary'],
                    json.dumps({
                        'input_id': input_entry['input_id'],
                        'relevance': input_entry['relevance'],
                        'summary_data': summary
                    }),
                    datetime.now()
                )
        except Exception as e:
            self.logger.error(f"Failed to store input analysis: {e}")
    
    # Query interface for other agents
    
    def query(self, query_type: str, **kwargs) -> Any:
        """
        Query interface for other agents to request information
        
        Examples:
        - query('system_mission')
        - query('all_components')
        - query('input_by_type', type='architecture_diagram')
        """
        if query_type == 'all_inputs':
            return list(self.inputs.values())
            
        elif query_type == 'input_by_type':
            input_type = kwargs.get('type')
            return [inp for inp in self.inputs.values() if inp.input_type == input_type]
            
        elif query_type == 'high_relevance_inputs':
            return [inp for inp in self.inputs.values() 
                   if inp.metadata.get('classification', {}).get('relevance') == 'high']
        
        elif query_type == 'system_description':
            # Return the most relevant system description
            desc_inputs = self.query('input_by_type', type='system_description')
            if desc_inputs:
                return desc_inputs[0].content
            # Fallback to any high relevance input
            high_rel = self.query('high_relevance_inputs')
            if high_rel:
                return high_rel[0].content
            return None
        
        elif query_type == 'input_content':
            # Get specific input content by ID
            input_id = kwargs.get('input_id')
            if input_id in self.inputs:
                return self.inputs[input_id].content
            return None
            
        else:
            self.logger.warning(f"Unknown query type: {query_type}")
            return None
    
    def get_input_summary_table(self) -> List[Dict[str, str]]:
        """Get summary table for display"""
        table_data = []
        for inp in self.inputs.values():
            table_data.append({
                'Input Name': Path(inp.source_path).name,
                'Type': inp.input_type.replace('_', ' ').title(),
                'Summary': inp.summary
                # Removed confidence - it was meaningless
            })
        return table_data