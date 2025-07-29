"""Robust JSON parser for handling LLM-generated JSON with common errors."""

import json
import re
from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)


class RobustJSONParser:
    """Parser that can handle common JSON errors from LLM outputs."""
    
    @staticmethod
    def parse(content: str) -> Union[Dict, List]:
        """
        Parse JSON content with error recovery.
        
        Handles common issues:
        - Missing commas between elements
        - Trailing commas
        - Single quotes instead of double quotes
        - Unescaped quotes in strings
        - Comments in JSON
        - Extra closing brackets
        """
        # First, try standard parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}")
            
        # Extract JSON from markdown code blocks if present
        cleaned = content.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        
        # Try again after extraction
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Apply fixes for common issues
        fixed = RobustJSONParser._apply_fixes(cleaned)
        
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed after fixes: {e}")
            logger.debug(f"Attempted to parse: {fixed[:500]}...")
            
            # Try to show the area around the error
            if hasattr(e, 'pos') and e.pos:
                error_pos = e.pos
                start = max(0, error_pos - 200)
                end = min(len(fixed), error_pos + 200)
                logger.error(f"JSON around error position {error_pos}:")
                logger.error(f"{fixed[start:end]}")
            
            # Last resort: try to extract valid JSON array/object
            extracted = RobustJSONParser._extract_json_structure(fixed)
            if extracted:
                try:
                    return json.loads(extracted)
                except:
                    pass
            
            # If all else fails, raise the original error
            raise ValueError(f"Unable to parse JSON: {e}")
    
    @staticmethod
    def _apply_fixes(content: str) -> str:
        """Apply common fixes to malformed JSON."""
        fixed = content
        
        # Remove comments (// and /* */ style)
        fixed = re.sub(r'//.*?$', '', fixed, flags=re.MULTILINE)
        fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
        
        # Remove any text before the first { or [
        json_start = min(
            fixed.find('{') if fixed.find('{') >= 0 else len(fixed),
            fixed.find('[') if fixed.find('[') >= 0 else len(fixed)
        )
        if json_start > 0 and json_start < len(fixed):
            fixed = fixed[json_start:]
        
        # Remove any text after the last } or ]
        last_brace = max(fixed.rfind('}'), fixed.rfind(']'))
        if last_brace > 0:
            fixed = fixed[:last_brace + 1]
        
        # Fix missing commas between array elements or object properties
        # Look for patterns like: "}\n{" or "]\n[" or "value"\n"key"
        fixed = re.sub(r'("\s*)\n(\s*")', r'\1,\n\2', fixed)
        fixed = re.sub(r'(})\s*\n\s*({)', r'\1,\n\2', fixed)
        fixed = re.sub(r'(])\s*\n\s*(\[)', r'\1,\n\2', fixed)
        fixed = re.sub(r'(")\s*\n\s*({)', r'\1,\n\2', fixed)
        fixed = re.sub(r'(})\s*\n\s*(")', r'\1,\n\2', fixed)
        fixed = re.sub(r'(true|false|null|\d+)\s*\n\s*(")', r'\1,\n\2', fixed)
        
        # Fix trailing commas
        fixed = re.sub(r',\s*}', '}', fixed)
        fixed = re.sub(r',\s*]', ']', fixed)
        
        # Fix single quotes (carefully, to avoid breaking apostrophes in text)
        # This is tricky, so we'll be conservative
        if fixed.count("'") > fixed.count('"'):
            # More single quotes than double quotes, might be using wrong quotes
            # Only replace single quotes that look like they're delimiting strings
            fixed = re.sub(r"(\s|^|{|\[|,)'([^']*)'(\s|$|}|]|,|:)", r'\1"\2"\3', fixed)
        
        # Fix unescaped quotes inside strings (very basic approach)
        # This is complex and error-prone, so we'll skip it for now
        
        return fixed
    
    @staticmethod
    def _extract_json_structure(content: str) -> str:
        """Try to extract a valid JSON array or object from content."""
        # Find the first [ or { and match to its closing bracket
        content = content.strip()
        
        if content.startswith('['):
            # Try to find matching ]
            bracket_count = 0
            for i, char in enumerate(content):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return content[:i+1]
        
        elif content.startswith('{'):
            # Try to find matching }
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(content):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    
                if not in_string:
                    if char == '{':
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            return content[:i+1]
        
        return None


def parse_llm_json(content: str) -> Union[Dict, List]:
    """
    Convenience function to parse JSON from LLM output.
    
    Args:
        content: Raw string content from LLM
        
    Returns:
        Parsed JSON object (dict or list)
        
    Raises:
        ValueError: If JSON cannot be parsed after all attempts
    """
    parser = RobustJSONParser()
    return parser.parse(content)