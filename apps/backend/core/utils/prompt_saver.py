"""
Prompt Saver utility for saving LLM prompts and responses during analysis.

This module provides a centralized way to save all prompts and responses
generated during STPA-Sec analysis for debugging and auditing purposes.
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging


class PromptSaver:
    """
    Saves prompts and responses to a structured directory for analysis debugging.
    
    Directory structure:
    output_dir/
    └── prompts/
        ├── step1_loss_identification_intuitive_001_prompt.txt
        ├── step1_loss_identification_intuitive_001_response.txt
        ├── step1_loss_identification_intuitive_001_metadata.json
        ├── step2_control_structure_balanced_001_prompt.txt
        └── ...
    """
    
    def __init__(self, output_dir: Path, enabled: bool = False):
        """
        Initialize the PromptSaver.
        
        Args:
            output_dir: Base output directory for the analysis
            enabled: Whether prompt saving is enabled (--save-prompts flag)
        """
        self.enabled = enabled
        self.output_dir = output_dir
        self.prompts_dir = output_dir / "prompts" if enabled else None
        self.counter = {}  # Track sequence numbers per agent
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if self.enabled and self.prompts_dir:
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Prompt saving enabled. Saving to: {self.prompts_dir}")
    
    def save_prompt_response(
        self,
        agent_name: str,
        cognitive_style: str,
        prompt: str,
        response: str,
        step: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Path]]:
        """
        Save a prompt and response pair.
        
        Args:
            agent_name: Name of the agent (e.g., "loss_identification", "control_structure_analyst")
            cognitive_style: Cognitive style used (e.g., "intuitive", "balanced")
            prompt: The prompt sent to the LLM
            response: The response received from the LLM
            step: STPA step number (1 or 2)
            metadata: Optional metadata about the prompt/response
            
        Returns:
            Dictionary with paths to saved files, or None if saving is disabled
        """
        if not self.enabled:
            return None
            
        # Generate unique key and increment counter
        key = f"step{step}_{agent_name}_{cognitive_style}"
        self.counter[key] = self.counter.get(key, 0) + 1
        sequence = str(self.counter[key]).zfill(3)
        
        # Create filenames
        base_name = f"{key}_{sequence}"
        prompt_file = self.prompts_dir / f"{base_name}_prompt.txt"
        response_file = self.prompts_dir / f"{base_name}_response.txt"
        metadata_file = self.prompts_dir / f"{base_name}_metadata.json"
        
        # Save prompt
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
            
        # Save response
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(response)
            
        # Save metadata
        full_metadata = {
            'agent_name': agent_name,
            'cognitive_style': cognitive_style,
            'step': step,
            'sequence': self.counter[key],
            'timestamp': datetime.now().isoformat(),
            'prompt_length': len(prompt),
            'response_length': len(response),
            'prompt_file': prompt_file.name,
            'response_file': response_file.name
        }
        if metadata:
            full_metadata.update(metadata)
            
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, indent=2)
            
        self.logger.debug(f"Saved prompt/response pair: {base_name}")
        
        return {
            'prompt_file': prompt_file,
            'response_file': response_file,
            'metadata_file': metadata_file
        }
    
    def save_conversation(
        self,
        agent_name: str,
        cognitive_style: str,
        messages: List[Dict[str, str]],
        step: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """
        Save a full conversation (multiple messages) as a single file.
        
        Args:
            agent_name: Name of the agent
            cognitive_style: Cognitive style used
            messages: List of message dictionaries with 'role' and 'content'
            step: STPA step number
            metadata: Optional metadata
            
        Returns:
            Path to saved conversation file, or None if disabled
        """
        if not self.enabled:
            return None
            
        key = f"step{step}_{agent_name}_{cognitive_style}_conversation"
        self.counter[key] = self.counter.get(key, 0) + 1
        sequence = str(self.counter[key]).zfill(3)
        
        filename = f"{key}_{sequence}.json"
        filepath = self.prompts_dir / filename
        
        conversation_data = {
            'agent_name': agent_name,
            'cognitive_style': cognitive_style,
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'messages': messages,
            'metadata': metadata or {}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2)
            
        return filepath
    
    def create_index(self) -> Optional[Path]:
        """
        Create an index file listing all saved prompts and responses.
        
        Returns:
            Path to the index file, or None if disabled
        """
        if not self.enabled or not self.prompts_dir:
            return None
            
        index_file = self.prompts_dir / "index.json"
        
        # Gather all metadata files
        metadata_files = sorted(self.prompts_dir.glob("*_metadata.json"))
        
        index_data = {
            'created_at': datetime.now().isoformat(),
            'total_prompts': len(metadata_files),
            'prompts': []
        }
        
        for metadata_file in metadata_files:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                index_data['prompts'].append(metadata)
                
        # Sort by timestamp
        index_data['prompts'].sort(key=lambda x: x['timestamp'])
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
            
        return index_file


# Singleton instance that can be initialized once per analysis
_prompt_saver: Optional[PromptSaver] = None


def init_prompt_saver(output_dir: Path, enabled: bool = False) -> PromptSaver:
    """Initialize the global prompt saver instance."""
    global _prompt_saver
    _prompt_saver = PromptSaver(output_dir, enabled)
    return _prompt_saver


def get_prompt_saver() -> Optional[PromptSaver]:
    """Get the global prompt saver instance."""
    return _prompt_saver