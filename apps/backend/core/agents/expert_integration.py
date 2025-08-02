"""
Integration layer between ExpertAgent and STPA-Sec analysis agents

Provides the glue code to enable ExpertAgent supervision of existing agents
with iterative refinement capabilities.
"""
from typing import Dict, Any, Optional, Type
import logging
from pathlib import Path

from .expert_agent import ExpertAgent, OperatingMode
from .step2_agents.base_step2 import BaseStep2Agent, AgentResult
from core.model_providers import BaseModelClient


class RefinableAgent:
    """
    Wrapper that makes existing agents refinable by ExpertAgent
    """
    
    def __init__(self, agent_class: Type[BaseStep2Agent], model_provider: BaseModelClient,
                 db_connection: Any, cognitive_style: Any):
        self.agent_class = agent_class
        self.model_provider = model_provider
        self.db_connection = db_connection
        self.cognitive_style = cognitive_style
        self.base_agent = agent_class(model_provider, db_connection, cognitive_style)
        self.refinement_history = []
        self.logger = logging.getLogger(f"Refinable{agent_class.__name__}")
        
    async def analyze_with_refinement(self, step1_analysis_id: str, step2_analysis_id: str,
                                    previous_results: Dict[str, Any],
                                    refinement_guidance: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Run analysis with optional refinement guidance from ExpertAgent
        """
        # If we have refinement guidance, enhance the agent's context
        if refinement_guidance:
            previous_results = self._apply_refinement_guidance(previous_results, refinement_guidance)
            
        # Run the base agent with potentially refined context
        result = await self.base_agent.analyze(
            step1_analysis_id=step1_analysis_id,
            step2_analysis_id=step2_analysis_id,
            previous_results=previous_results
        )
        
        # Track refinement history
        if refinement_guidance:
            self.refinement_history.append({
                "guidance": refinement_guidance,
                "result": result
            })
            
        return result
        
    def _apply_refinement_guidance(self, previous_results: Dict[str, Any],
                                 refinement_guidance: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ExpertAgent refinement guidance to the analysis context"""
        
        enhanced_results = previous_results.copy()
        
        # Add refinement instructions to context
        enhanced_results["expert_refinement"] = {
            "priority_fixes": refinement_guidance.get("priority_fixes", []),
            "avoid_patterns": refinement_guidance.get("avoid_patterns", []),
            "specific_requirements": refinement_guidance.get("prompt_additions", [])
        }
        
        # Add examples if provided
        if "context_enhancements" in refinement_guidance:
            enhancements = refinement_guidance["context_enhancements"]
            if "add_examples" in enhancements:
                enhanced_results["expert_examples"] = enhancements["add_examples"]
            if "clarify_requirements" in enhancements:
                enhanced_results["clarified_requirements"] = enhancements["clarify_requirements"]
                
        return enhanced_results


class ExpertSupervisedCoordinator:
    """
    Enhanced Step2Coordinator that uses ExpertAgent for quality control
    """
    
    def __init__(self, base_coordinator, expert_agent: ExpertAgent):
        self.base_coordinator = base_coordinator
        self.expert_agent = expert_agent
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def coordinate_with_supervision(self, step1_analysis_id: str, 
                                         execution_mode: str = 'standard',
                                         max_refinements: int = 3) -> Dict[str, Any]:
        """
        Run Step 2 coordination with ExpertAgent supervision
        """
        # Initialize Step 2 analysis (mimics base coordinator initialization)
        step2_analysis_id = await self.base_coordinator._create_step2_analysis(step1_analysis_id, execution_mode)
        self.base_coordinator.current_step2_id = step2_analysis_id
        
        # Track supervision results
        supervision_results = {}
        
        # Execute phases with supervision
        phase_results = {}
        
        for phase in self.base_coordinator.phases:
            self.logger.info(f"Executing Step 2 phase with supervision: {phase['name']}")
            
            # Run the phase
            if phase.get('parallel', False):
                results = await self._execute_parallel_with_supervision(
                    phase, step1_analysis_id, phase_results, max_refinements
                )
            else:
                results = await self._execute_sequential_with_supervision(
                    phase, step1_analysis_id, phase_results, max_refinements
                )
                
            phase_results[phase['name']] = results['outputs']
            supervision_results[phase['name']] = results['supervision']
            
        # Final synthesis with quality check
        synthesis = await self._synthesize_with_quality_check(phase_results)
        
        # Store final results
        await self.base_coordinator._store_final_results(step2_analysis_id, synthesis)
        
        return {
            "analysis_id": step2_analysis_id,
            "phase_results": phase_results,
            "supervision_results": supervision_results,
            "synthesis": synthesis,
            "overall_quality": self._calculate_overall_quality(supervision_results)
        }
        
    async def _execute_sequential_with_supervision(self, phase: Dict[str, Any],
                                                 step1_analysis_id: str,
                                                 previous_results: Dict[str, Any],
                                                 max_refinements: int) -> Dict[str, Any]:
        """Execute agents sequentially with expert supervision"""
        
        outputs = {}
        supervision = {}
        
        for agent_name in phase['agents']:
            # Create refinable agent wrapper
            agent = self._create_refinable_agent(agent_name)
            
            # Initial analysis
            initial_result = await agent.analyze_with_refinement(
                step1_analysis_id=step1_analysis_id,
                step2_analysis_id=self.base_coordinator.current_step2_id,
                previous_results=previous_results
            )
            
            # Expert supervision (clean data for JSON serialization)
            clean_output = self._make_serializable(initial_result.data)
            supervision_result = await self.expert_agent.supervise_step_analysis(
                step_number=2,
                agent_type=agent_name,
                initial_output=clean_output,
                context=previous_results,
                max_retries=max_refinements
            )
            
            # If refinement was needed, run refined analysis
            if supervision_result["retry_count"] > 0:
                final_guidance = supervision_result.get("final_refinement_guidance")
                if final_guidance:
                    refined_result = await agent.analyze_with_refinement(
                        step1_analysis_id=step1_analysis_id,
                        step2_analysis_id=self.base_coordinator.current_step2_id,
                        previous_results=previous_results,
                        refinement_guidance=final_guidance
                    )
                    outputs[agent_name] = refined_result
                else:
                    outputs[agent_name] = initial_result
            else:
                outputs[agent_name] = initial_result
                
            supervision[agent_name] = supervision_result
            
        return {
            "outputs": outputs,
            "supervision": supervision
        }
        
    async def _execute_parallel_with_supervision(self, phase: Dict[str, Any],
                                               step1_analysis_id: str,
                                               previous_results: Dict[str, Any],
                                               max_refinements: int) -> Dict[str, Any]:
        """Execute agents in parallel with expert supervision"""
        
        # For parallel execution, run initial analysis for all agents first
        # Then supervise and refine as needed
        # Implementation similar to sequential but with asyncio.gather
        
        # Placeholder for now
        return await self._execute_sequential_with_supervision(
            phase, step1_analysis_id, previous_results, max_refinements
        )
        
    def _create_refinable_agent(self, agent_name: str) -> RefinableAgent:
        """Create a refinable wrapper for an agent"""
        
        agent_class = self.base_coordinator.agent_classes.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        return RefinableAgent(
            agent_class=agent_class,
            model_provider=self.base_coordinator.model_provider,
            db_connection=self.base_coordinator.db_connection,
            cognitive_style=self.base_coordinator.cognitive_style
        )
        
    async def _synthesize_with_quality_check(self, phase_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results with quality validation"""
        
        synthesis = await self.base_coordinator._synthesize_results(
            self.base_coordinator.current_step2_id, phase_results
        )
        
        # Check synthesis quality
        quality_check = await self.expert_agent.assess_output_quality(
            step_number=2,
            agent_type="synthesis",
            output=synthesis,
            context=phase_results
        )
        
        synthesis["quality_assessment"] = quality_check
        
        return synthesis
        
    def _calculate_overall_quality(self, supervision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall quality metrics from supervision results"""
        
        total_agents = 0
        quality_scores = []
        total_refinements = 0
        issues_by_type = {}
        
        for phase, phase_supervision in supervision_results.items():
            for agent, supervision in phase_supervision.items():
                total_agents += 1
                total_refinements += supervision.get("retry_count", 0)
                
                assessment = supervision.get("quality_assessment", {})
                if "overall_score" in assessment:
                    quality_scores.append(assessment["overall_score"])
                    
                for issue in assessment.get("issues", []):
                    issue_type = issue.get("type", "unknown")
                    issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
                    
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "average_quality_score": avg_quality,
            "total_refinements": total_refinements,
            "agents_analyzed": total_agents,
            "common_issues": issues_by_type,
            "quality_level": self._determine_overall_quality_level(avg_quality)
        }
        
    def _make_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make data JSON serializable by removing non-serializable objects"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'component_registry':
                    # Skip ComponentRegistry objects
                    continue
                elif isinstance(value, dict):
                    result[key] = self._make_serializable(value)
                elif isinstance(value, list):
                    result[key] = [self._make_serializable(item) if isinstance(item, dict) else item for item in value]
                else:
                    try:
                        # Test if it's JSON serializable
                        import json
                        json.dumps(value)
                        result[key] = value
                    except (TypeError, ValueError):
                        # Skip non-serializable values
                        continue
            return result
        return data
    
    def _determine_overall_quality_level(self, avg_score: float) -> str:
        """Determine overall quality level from average score"""
        if avg_score >= 0.9:
            return "excellent"
        elif avg_score >= 0.7:
            return "acceptable"
        elif avg_score >= 0.5:
            return "needs_improvement"
        else:
            return "unacceptable"


def create_expert_supervised_coordinator(base_coordinator, model_provider: BaseModelClient,
                                       knowledge_dir: Path,
                                       operating_mode: OperatingMode = OperatingMode.HUMAN_IN_LOOP):
    """
    Factory function to create an expert-supervised coordinator
    """
    expert_agent = ExpertAgent(
        model_provider=model_provider,
        knowledge_dir=knowledge_dir,
        operating_mode=operating_mode
    )
    
    return ExpertSupervisedCoordinator(
        base_coordinator=base_coordinator,
        expert_agent=expert_agent
    )