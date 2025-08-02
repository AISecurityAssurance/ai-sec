"""
Expert Agent for STPA-Sec Methodology Compliance and Quality Control

The ExpertAgent acts as an AI-in-the-loop quality controller, ensuring that
all analysis steps follow current STPA-Sec methodology and best practices.
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import asyncio
from pathlib import Path
from datetime import datetime
from enum import Enum
import logging

from core.utils.json_parser import parse_llm_json
from core.model_providers import BaseModelClient, ModelResponse


class OperatingMode(Enum):
    """System operating modes"""
    HUMAN_IN_LOOP = "human_in_loop"          # Human reviews each step
    HUMAN_AFTER_LOOP = "human_after_loop"    # Human reviews after full analysis
    FULLY_AUTOMATED = "fully_automated"       # No human intervention


class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"    # Meets all standards
    ACCEPTABLE = "acceptable"  # Minor issues but can proceed
    NEEDS_IMPROVEMENT = "needs_improvement"  # Major issues, should refine
    UNACCEPTABLE = "unacceptable"  # Critical violations, must retry


class ExpertAgent:
    """
    Expert Agent that supervises and improves analysis quality using
    methodology knowledge and iterative refinement.
    """
    
    def __init__(self, model_provider: BaseModelClient, knowledge_dir: Path, 
                 operating_mode: OperatingMode = OperatingMode.HUMAN_IN_LOOP):
        self.model_provider = model_provider
        self.knowledge_dir = knowledge_dir
        self.operating_mode = operating_mode
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load expert knowledge
        self.knowledge_base = self._load_knowledge_base()
        self.quality_standards = self._load_quality_standards()
        self.common_errors = self._load_common_error_patterns()
        
        # Configure behavior based on operating mode
        self._configure_for_mode(operating_mode)
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load methodology documents and guidelines"""
        knowledge = {
            "stpa_principles": self._load_stpa_principles(),
            "step_requirements": self._load_step_requirements(),
            "abstraction_guidelines": self._load_abstraction_guidelines(),
            "quality_standards": self._load_quality_standards(),
            "common_error_patterns": self._load_common_error_patterns()
        }
        
        # Load documents from knowledge directory if available
        if self.knowledge_dir.exists():
            for doc_path in self.knowledge_dir.glob("*.md"):
                doc_name = doc_path.stem
                with open(doc_path, 'r') as f:
                    knowledge[doc_name] = f.read()
                    
        return knowledge
        
    def _load_stpa_principles(self) -> Dict[str, str]:
        """Core STPA-Sec principles"""
        return {
            "control_loops": "Every control action must have corresponding feedback",
            "hierarchy": "Higher levels have authority over lower levels",
            "abstraction": "Use service-level abstraction, not implementation details",
            "completeness": "All system components must be part of control structure",
            "trust_boundaries": "Identify where authentication/authorization changes"
        }
        
    def _load_step_requirements(self) -> Dict[int, Dict[str, Any]]:
        """Requirements for each STPA-Sec step"""
        return {
            1: {
                "outputs": ["losses", "hazards", "constraints", "stakeholders"],
                "quality_checks": [
                    "Losses tied to mission/business objectives",
                    "Hazards lead to losses",
                    "Constraints prevent hazards",
                    "Stakeholders have defined responsibilities"
                ]
            },
            2: {
                "outputs": ["control_structure", "control_actions", "feedback", "trust_boundaries"],
                "quality_checks": [
                    "Components at appropriate abstraction level",
                    "All control loops closed with feedback",
                    "Trust boundaries at authentication/authorization changes",
                    "Process models include state variables and assumptions"
                ]
            }
        }
        
    def _load_abstraction_guidelines(self) -> Dict[str, Any]:
        """Guidelines for appropriate abstraction levels"""
        return {
            "sd_wan": {
                "good": ["SD-WAN Controller", "Edge Gateway", "Network Management Console"],
                "too_detailed": ["Routing Table", "Policy Rules", "TCP Settings"],
                "too_generic": ["Network", "Security System", "Management"]
            },
            "general": {
                "service_level": "Components that make independent decisions",
                "avoid": "Implementation details, parameters, specific configurations"
            }
        }
        
    def _load_quality_standards(self) -> Dict[str, Any]:
        """Quality standards for each analysis aspect"""
        return {
            "control_structure": {
                "min_components": 3,
                "max_hierarchy_depth": 5,
                "required_types": ["controller", "controlled_process"]
            },
            "control_actions": {
                "specificity": "Specific enough to identify meaningful impacts",
                "examples": {
                    "good": ["Configure Traffic Routing Policy", "Authorize Network Access"],
                    "bad": ["Manage Network", "Control System"]
                }
            },
            "feedback": {
                "required_types": ["explicit", "implicit", "positive", "error"],
                "control_loop_closure": "Every control action needs feedback path"
            }
        }
        
    def _load_common_error_patterns(self) -> List[Dict[str, Any]]:
        """Common errors and how to fix them"""
        return [
            {
                "pattern": "missing_feedback",
                "description": "Control actions without feedback mechanisms",
                "fix": "Identify how controller knows action was successful"
            },
            {
                "pattern": "wrong_abstraction",
                "description": "Components too detailed or too generic",
                "fix": "Focus on decision-making entities, not implementations"
            },
            {
                "pattern": "undefined_components",
                "description": "References to components not in control structure",
                "fix": "Ensure all referenced components are defined"
            }
        ]
        
    def _make_json_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        import json
        if hasattr(obj, 'value'):  # Handle enums
            return obj.value
        elif hasattr(obj, 'dict'):  # Handle AgentResult and similar objects with dict() method
            return self._make_json_serializable(obj.dict())
        elif hasattr(obj, '__dict__'):  # Handle custom objects with attributes
            return self._make_json_serializable(obj.__dict__)
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            try:
                # Test if it's already JSON serializable
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # Skip non-serializable values
                return str(obj)  # Convert to string as fallback
    
    def _configure_for_mode(self, mode: OperatingMode):
        """Configure behavior based on operating mode"""
        if mode == OperatingMode.HUMAN_IN_LOOP:
            self.validation_strictness = "high"
            self.max_auto_retries = 2
            self.provide_detailed_feedback = True
            self.continue_on_warnings = False
            
        elif mode == OperatingMode.HUMAN_AFTER_LOOP:
            self.validation_strictness = "medium"
            self.max_auto_retries = 3
            self.provide_detailed_feedback = True
            self.continue_on_warnings = True
            
        elif mode == OperatingMode.FULLY_AUTOMATED:
            self.validation_strictness = "conservative"
            self.max_auto_retries = 5
            self.provide_detailed_feedback = False
            self.continue_on_warnings = True
            
    async def supervise_step_analysis(self, step_number: int, agent_type: str,
                                    initial_output: Dict[str, Any], context: Dict[str, Any],
                                    max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Supervise and iteratively improve step analysis output.
        
        Args:
            step_number: STPA-Sec step number (1-5)
            agent_type: Type of agent that produced the output
            initial_output: Initial agent output to assess
            context: Analysis context including previous steps
            max_retries: Override default max retries
            
        Returns:
            Dict containing final output and quality assessment
        """
        if max_retries is None:
            max_retries = self.max_auto_retries
            
        current_output = initial_output
        retry_count = 0
        iteration_history = []
        
        while retry_count <= max_retries:
            # Assess output quality
            quality_assessment = await self.assess_output_quality(
                step_number, agent_type, current_output, context
            )
            
            # Log iteration
            iteration_history.append({
                "iteration": retry_count,
                "quality": quality_assessment["quality_level"],
                "issues": quality_assessment["issues"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if quality is acceptable
            if quality_assessment["quality_level"] in [QualityLevel.EXCELLENT, QualityLevel.ACCEPTABLE]:
                if quality_assessment["quality_level"] == QualityLevel.ACCEPTABLE and not self.continue_on_warnings:
                    # In human-in-loop mode, ask for confirmation
                    quality_assessment["requires_confirmation"] = True
                    
                return {
                    "final_output": current_output,
                    "quality_assessment": quality_assessment,
                    "iteration_history": iteration_history,
                    "retry_count": retry_count,
                    "success": True
                }
            
            # Generate refinement guidance
            refinement_guidance = await self.generate_refinement_guidance(
                step_number, agent_type, quality_assessment, retry_count
            )
            
            # Check if we should continue
            if retry_count >= max_retries:
                self.logger.warning(f"Max retries ({max_retries}) reached for {agent_type}")
                break
                
            # Request refined output
            refined_output = await self.request_refined_output(
                agent_type, current_output, refinement_guidance, context
            )
            
            if refined_output:
                current_output = refined_output
                retry_count += 1
            else:
                self.logger.error(f"Failed to get refined output from {agent_type}")
                break
                
        # Max retries reached or refinement failed
        return {
            "final_output": current_output,
            "quality_assessment": quality_assessment,
            "iteration_history": iteration_history,
            "retry_count": retry_count,
            "success": False,
            "warning": "Quality standards not fully met"
        }
        
    async def assess_output_quality(self, step_number: int, agent_type: str,
                                  output: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the quality of agent output against methodology standards.
        """
        assessment_prompt = self._build_assessment_prompt(step_number, agent_type, output, context)
        
        messages = [
            {"role": "system", "content": "You are an STPA-Sec methodology expert assessing analysis quality."},
            {"role": "user", "content": assessment_prompt}
        ]
        response = await self.model_provider.generate(
            messages,
            temperature=0.3
        )
        
        try:
            assessment = parse_llm_json(response.content)
            # Convert quality level string to enum
            assessment["quality_level"] = QualityLevel(assessment.get("quality_level", "needs_improvement"))
            return assessment
        except Exception as e:
            self.logger.error(f"Failed to parse quality assessment: {e}")
            return {
                "quality_level": QualityLevel.NEEDS_IMPROVEMENT,
                "issues": [{"type": "assessment_error", "description": str(e)}],
                "recommendations": ["Manual review required"]
            }
            
    def _build_assessment_prompt(self, step_number: int, agent_type: str,
                               output: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for quality assessment"""
        
        step_requirements = self.knowledge_base["step_requirements"].get(step_number, {})
        quality_standards = self.quality_standards
        
        prompt = f"""
You are assessing the quality of STPA-Sec Step {step_number} output from {agent_type}.

## Methodology Requirements for Step {step_number}:
{json.dumps(step_requirements, indent=2)}

## Quality Standards:
{json.dumps(quality_standards, indent=2)}

## Output to Assess:
{json.dumps(self._make_json_serializable(output), indent=2)}

## Previous Analysis Context:
{json.dumps(self._make_json_serializable(context), indent=2)}

## Your Task:
Assess the output quality and provide:

1. Overall quality level: "excellent", "acceptable", "needs_improvement", or "unacceptable"
2. Specific issues found (if any)
3. Recommendations for improvement
4. Methodology compliance check

Return your assessment as JSON:
{{
    "quality_level": "excellent|acceptable|needs_improvement|unacceptable",
    "overall_score": 0.0-1.0,
    "methodology_compliance": {{
        "follows_stpa_principles": true/false,
        "meets_step_requirements": true/false,
        "appropriate_abstraction": true/false,
        "complete_control_loops": true/false
    }},
    "issues": [
        {{
            "type": "issue_type",
            "severity": "critical|major|minor",
            "description": "what is wrong",
            "location": "where in the output",
            "fix_guidance": "how to fix it"
        }}
    ],
    "strengths": ["what was done well"],
    "recommendations": ["specific improvements needed"],
    "missing_elements": ["required elements not found"]
}}
"""
        return prompt
        
    async def generate_refinement_guidance(self, step_number: int, agent_type: str,
                                         quality_assessment: Dict[str, Any],
                                         retry_count: int) -> Dict[str, Any]:
        """Generate specific guidance for improving the output"""
        
        # Convert quality assessment to JSON-serializable format
        serializable_assessment = self._make_json_serializable(quality_assessment)
        
        guidance_prompt = f"""
Based on this quality assessment for STPA-Sec Step {step_number}, generate specific refinement guidance.

## Quality Assessment:
{json.dumps(serializable_assessment, indent=2)}

## Current Retry: {retry_count}

## Common Error Patterns:
{json.dumps(self.common_errors, indent=2)}

Generate specific, actionable guidance for the {agent_type} to improve its output.
Focus on the most critical issues first.

Return guidance as JSON:
{{
    "priority_fixes": [
        {{
            "issue": "what to fix",
            "specific_guidance": "exactly how to fix it",
            "example": "example of correct approach"
        }}
    ],
    "prompt_additions": ["specific instructions to add to prompt"],
    "context_enhancements": {{
        "add_examples": ["helpful examples"],
        "clarify_requirements": ["requirements to emphasize"]
    }},
    "avoid_patterns": ["patterns to avoid"]
}}
"""
        
        messages = [
            {"role": "system", "content": "You are an STPA-Sec expert providing specific improvement guidance."},
            {"role": "user", "content": guidance_prompt}
        ]
        response = await self.model_provider.generate(
            messages,
            temperature=0.3
        )
        
        try:
            return parse_llm_json(response.content)
        except Exception as e:
            self.logger.error(f"Failed to parse refinement guidance: {e}")
            return {
                "priority_fixes": [{"issue": "General improvement", "specific_guidance": "Review and refine output"}],
                "prompt_additions": []
            }
            
    async def request_refined_output(self, agent_type: str, current_output: Dict[str, Any],
                                   refinement_guidance: Dict[str, Any],
                                   context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Request refined output from the original agent"""
        
        # This would integrate with the actual agent to request refinement
        # For now, returning None to indicate this needs agent integration
        self.logger.info(f"Would request refinement from {agent_type} with guidance: {refinement_guidance}")
        return None
        
    def generate_quality_report(self, supervision_result: Dict[str, Any]) -> str:
        """Generate human-readable quality report"""
        
        report = f"""
# STPA-Sec Analysis Quality Report

## Summary
- Final Quality Level: {supervision_result['quality_assessment']['quality_level'].value}
- Iterations Required: {supervision_result['retry_count']}
- Success: {'Yes' if supervision_result['success'] else 'No - Manual Review Required'}

## Quality Assessment
"""
        
        assessment = supervision_result['quality_assessment']
        
        if 'methodology_compliance' in assessment:
            report += "\n### Methodology Compliance\n"
            for check, passed in assessment['methodology_compliance'].items():
                status = "✓" if passed else "✗"
                report += f"- {status} {check.replace('_', ' ').title()}\n"
                
        if 'issues' in assessment and assessment['issues']:
            report += "\n### Issues Found\n"
            for issue in assessment['issues']:
                report += f"\n**{issue['severity'].upper()}: {issue['type']}**\n"
                report += f"- Description: {issue['description']}\n"
                if 'fix_guidance' in issue:
                    report += f"- Fix: {issue['fix_guidance']}\n"
                    
        if 'strengths' in assessment and assessment['strengths']:
            report += "\n### Strengths\n"
            for strength in assessment['strengths']:
                report += f"- {strength}\n"
                
        if 'recommendations' in assessment and assessment['recommendations']:
            report += "\n### Recommendations\n"
            for rec in assessment['recommendations']:
                report += f"- {rec}\n"
                
        if 'iteration_history' in supervision_result:
            report += "\n## Iteration History\n"
            for iteration in supervision_result['iteration_history']:
                report += f"\n### Iteration {iteration['iteration']}\n"
                report += f"- Quality: {iteration['quality']}\n"
                report += f"- Issues: {len(iteration['issues'])}\n"
                
        return report