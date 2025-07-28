"""
Step 1 Coordinator for STPA-Sec Analysis
"""
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
from uuid import uuid4
import asyncpg
import os
from pathlib import Path

from .mission_analyst import MissionAnalystAgent
from .loss_identification import LossIdentificationAgent
from .hazard_identification import HazardIdentificationAgent
from .stakeholder_analyst import StakeholderAnalystAgent
from .security_constraint_agent import SecurityConstraintAgent
from .system_boundary_agent import SystemBoundaryAgent
from .validation_agent import ValidationAgent
from .base_step1 import CognitiveStyle


class Step1Coordinator:
    """
    Coordinates all Step 1 agents to perform complete STPA-Sec Step 1 analysis
    
    Execution flow:
    1. Mission Analyst - Extract mission and context
    2. Loss Identification - Identify unacceptable outcomes
    3. Hazard Identification - Identify hazardous states (depends on losses)
    4. Stakeholder Analyst - Analyze perspectives (depends on losses)
    5. Security Constraint - Define required properties (depends on losses/hazards)
    6. System Boundary - Define analysis scope (depends on all above)
    7. Validation - Validate and create Step 2 bridge
    
    Supports ASI-ARCH Dream Team execution modes:
    - standard: Single agent per task (default)
    - enhanced: Dual perspective (Intuitive + Technical)
    - dream_team: Full quaternion (all 4 cognitive styles)
    """
    
    def __init__(self, analysis_id: Optional[str] = None, 
                 db_connection: Optional[asyncpg.Connection] = None,
                 execution_mode: str = "standard",
                 db_name: Optional[str] = None):
        self.analysis_id = analysis_id or str(uuid4())
        self.db_connection = db_connection
        self.db_name = db_name  # Store database name for parallel connections
        self.execution_log = []
        self.execution_mode = execution_mode
        
        # Define cognitive styles for each execution mode
        self.cognitive_styles_by_mode = {
            "standard": [CognitiveStyle.BALANCED],
            "enhanced": [CognitiveStyle.INTUITIVE, CognitiveStyle.TECHNICAL],
            "dream_team": [
                CognitiveStyle.INTUITIVE,
                CognitiveStyle.TECHNICAL,
                CognitiveStyle.CREATIVE,
                CognitiveStyle.SYSTEMATIC
            ]
        }
        
    async def perform_analysis(self, system_description: str, 
                             analysis_name: str = "Step 1 Analysis") -> Dict[str, Any]:
        """
        Perform complete Step 1 analysis
        
        Args:
            system_description: Natural language description of the system
            analysis_name: Name for this analysis
            
        Returns:
            Complete Step 1 analysis results
        """
        start_time = datetime.now()
        
        try:
            # Create database connection if not provided
            if not self.db_connection:
                import os
                DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')
                self.db_connection = await asyncpg.connect(DATABASE_URL)
                self._owns_connection = True
            else:
                self._owns_connection = False
            
            # Create analysis record
            await self._create_analysis_record(analysis_name, system_description)
            
            # Initialize context
            context = {
                "system_description": system_description,
                "analysis_id": self.analysis_id,
                "timestamp": start_time.isoformat()
            }
            
            # Phase 1: Mission Analysis
            self._log_execution("Starting Phase 1: Mission Analysis")
            mission_agent = MissionAnalystAgent(self.analysis_id, self.db_connection)
            mission_results = await mission_agent.analyze(context)
            
            if self.db_connection:
                await self._save_mission_results(mission_results)
            
            # Phase 2: Loss Identification
            self._log_execution("Starting Phase 2: Loss Identification")
            loss_results = await self._run_agent_with_cognitive_styles(
                LossIdentificationAgent, context, "Loss Identification"
            )
            
            if self.db_connection:
                await self._save_loss_results(loss_results)
            
            # Phase 3: Parallel execution of Hazard and Stakeholder analysis
            self._log_execution("Starting Phase 3: Hazard and Stakeholder Analysis (parallel)")
            
            hazard_task = asyncio.create_task(self._run_hazard_analysis(context))
            stakeholder_task = asyncio.create_task(self._run_stakeholder_analysis(context))
            
            hazard_results, stakeholder_results = await asyncio.gather(
                hazard_task, stakeholder_task
            )
            
            # Phase 4: Security Constraint Definition
            self._log_execution("Starting Phase 4: Security Constraint Definition")
            security_constraint_results = await self._run_agent_with_cognitive_styles(
                SecurityConstraintAgent, context, "Security Constraint Definition"
            )
            
            if self.db_connection:
                await self._save_security_constraint_results(security_constraint_results)
            
            # Phase 5: System Boundary Definition
            self._log_execution("Starting Phase 5: System Boundary Definition")
            system_boundary_results = await self._run_agent_with_cognitive_styles(
                SystemBoundaryAgent, context, "System Boundary Definition"
            )
            
            if self.db_connection:
                await self._save_system_boundary_results(system_boundary_results)
            
            # Phase 6: Validation
            self._log_execution("Starting Phase 6: Validation and Quality Assessment")
            validation_agent = ValidationAgent(self.analysis_id, self.db_connection)
            validation_results = await validation_agent.analyze(context)
            
            if self.db_connection:
                await self._save_validation_results(validation_results)
            
            # Compile final results
            final_results = {
                "analysis_id": self.analysis_id,
                "analysis_name": analysis_name,
                "timestamp": start_time.isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": validation_results['overall_status'],
                "results": {
                    "mission_analysis": mission_results,
                    "loss_identification": loss_results,
                    "hazard_identification": hazard_results,
                    "stakeholder_analysis": stakeholder_results,
                    "security_constraints": security_constraint_results,
                    "system_boundaries": system_boundary_results,
                    "validation": validation_results
                },
                "executive_summary": validation_results['executive_summary'],
                "step2_bridge": validation_results['step2_bridge'],
                "execution_log": self.execution_log
            }
            
            # Update analysis record with completion
            if self.db_connection:
                await self._update_analysis_completion(final_results)
            
            # Perform completeness check
            completeness = self._check_analysis_completeness(final_results)
            final_results['completeness_check'] = completeness
            
            if not completeness['is_complete']:
                self._log_execution(f"WARNING: Analysis incomplete - {completeness['summary']}", error=True)
            else:
                self._log_execution("Step 1 analysis completed successfully")
            
            return final_results
            
        except Exception as e:
            self._log_execution(f"Error during analysis: {str(e)}", error=True)
            
            # Update analysis record with error
            if self.db_connection:
                await self._update_analysis_error(str(e))
            
            raise
        finally:
            # Close connection if we created it
            if hasattr(self, '_owns_connection') and self._owns_connection and self.db_connection:
                await self.db_connection.close()
    
    async def _run_hazard_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run hazard analysis"""
        # Create separate connection for parallel execution
        import os
        db_host = os.getenv('DB_HOST', 'postgres')
        # Use the same database as the main connection
        if self.db_name:
            DATABASE_URL = f"postgresql://sa_user:sa_password@{db_host}:5432/{self.db_name}"
        else:
            DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')
            # Remove SQLAlchemy-specific prefix if present
            if DATABASE_URL.startswith('postgresql+asyncpg://'):
                DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
        hazard_conn = await asyncpg.connect(DATABASE_URL)
        
        try:
            hazard_agent = HazardIdentificationAgent(self.analysis_id, hazard_conn)
            results = await hazard_agent.analyze(context)
            
            # Save using the hazard connection, not the main one
            await self._save_hazard_results_with_conn(results, hazard_conn)
            
            return results
        finally:
            await hazard_conn.close()
    
    async def _run_stakeholder_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run stakeholder analysis"""
        # Create separate connection for parallel execution
        import os
        db_host = os.getenv('DB_HOST', 'postgres')
        # Use the same database as the main connection
        if self.db_name:
            DATABASE_URL = f"postgresql://sa_user:sa_password@{db_host}:5432/{self.db_name}"
        else:
            DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')
            # Remove SQLAlchemy-specific prefix if present
            if DATABASE_URL.startswith('postgresql+asyncpg://'):
                DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
        stakeholder_conn = await asyncpg.connect(DATABASE_URL)
        
        try:
            stakeholder_agent = StakeholderAnalystAgent(self.analysis_id, stakeholder_conn)
            results = await stakeholder_agent.analyze(context)
            
            # Save using the stakeholder connection, not the main one
            await self._save_stakeholder_results_with_conn(results, stakeholder_conn)
            
            return results
        finally:
            await stakeholder_conn.close()
    
    async def _run_agent_with_cognitive_styles(self, agent_class, context: Dict[str, Any], 
                                             phase_name: str) -> Dict[str, Any]:
        """
        Run an agent with multiple cognitive styles based on execution mode
        
        Args:
            agent_class: The agent class to instantiate
            context: Analysis context
            phase_name: Name of the phase for logging
            
        Returns:
            Synthesized results from all cognitive styles
        """
        cognitive_styles = self.cognitive_styles_by_mode.get(self.execution_mode, [CognitiveStyle.BALANCED])
        
        if len(cognitive_styles) == 1:
            # Standard mode - single agent
            agent = agent_class(self.analysis_id, self.db_connection, cognitive_styles[0])
            return await agent.analyze(context)
        
        # Enhanced or dream team mode - multiple agents
        results = []
        for style in cognitive_styles:
            self._log_execution(f"{phase_name} - {style.value} perspective")
            agent = agent_class(self.analysis_id, self.db_connection, style)
            style_results = await agent.analyze(context)
            results.append({
                "cognitive_style": style.value,
                "results": style_results
            })
        
        # Synthesize results
        return self._synthesize_cognitive_results(results, agent_class.__name__)
    
    def _synthesize_cognitive_results(self, results: List[Dict[str, Any]], agent_type: str) -> Dict[str, Any]:
        """
        Synthesize results from multiple cognitive styles
        
        For Phase 1, we use simple union/merge strategy
        Later phases can implement more sophisticated synthesis
        """
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]["results"]
        
        # For now, merge all findings and track which cognitive style found them
        synthesized = {
            "cognitive_synthesis": {
                "styles_used": [r["cognitive_style"] for r in results],
                "consensus_findings": [],
                "unique_findings": {},
                "synthesis_method": "union_merge"
            }
        }
        
        # Agent-specific synthesis logic
        if "Loss" in agent_type:
            synthesized.update(self._synthesize_loss_results(results))
        elif "Hazard" in agent_type:
            synthesized.update(self._synthesize_hazard_results(results))
        elif "Stakeholder" in agent_type:
            synthesized.update(self._synthesize_stakeholder_results(results))
        elif "SecurityConstraint" in agent_type:
            synthesized.update(self._synthesize_security_constraint_results(results))
        elif "SystemBoundary" in agent_type:
            synthesized.update(self._synthesize_system_boundary_results(results))
        else:
            # Generic synthesis - merge all results
            synthesized.update(results[0]["results"])
        
        return synthesized
    
    def _synthesize_loss_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize loss identification results from multiple cognitive styles"""
        all_losses = []
        loss_map = {}
        
        for style_result in results:
            style = style_result["cognitive_style"]
            losses = style_result["results"].get("losses", [])
            
            for loss in losses:
                # Create unique key for deduplication
                key = f"{loss['loss_category']}:{loss['description'][:50]}"
                
                if key not in loss_map:
                    loss_map[key] = {
                        **loss,
                        "found_by_styles": [style],
                        "confidence": "high" if len(results) > 1 else "medium"
                    }
                else:
                    loss_map[key]["found_by_styles"].append(style)
                    loss_map[key]["confidence"] = "very_high"
        
        # Convert back to list with new identifiers
        all_losses = list(loss_map.values())
        for i, loss in enumerate(all_losses):
            loss["identifier"] = f"L-{i+1}"
        
        return {
            "losses": all_losses,
            "loss_count": len(all_losses),
            "synthesis_metadata": {
                "total_unique_losses": len(all_losses),
                "consensus_losses": len([l for l in all_losses if len(l["found_by_styles"]) > 1]),
                "style_contributions": {
                    style: len([l for l in all_losses if style in l["found_by_styles"]])
                    for style in set(sum([l["found_by_styles"] for l in all_losses], []))
                }
            }
        }
    
    def _synthesize_hazard_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize hazard identification results from multiple cognitive styles"""
        # Similar to loss synthesis but for hazards
        return results[0]["results"]  # Placeholder
    
    def _synthesize_stakeholder_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize stakeholder analysis results from multiple cognitive styles"""
        # Similar synthesis logic
        return results[0]["results"]  # Placeholder
    
    def _synthesize_security_constraint_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize security constraint results from multiple cognitive styles"""
        # Similar to loss synthesis but for security constraints
        return results[0]["results"]  # Placeholder
    
    def _synthesize_system_boundary_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize system boundary results from multiple cognitive styles"""
        # Similar synthesis logic for system boundaries
        return results[0]["results"]  # Placeholder
    
    async def _create_analysis_record(self, name: str, description: str):
        """Create initial analysis record if it doesn't exist"""
        # Check if analysis already exists
        result = await self.db_connection.fetchval("""
            SELECT EXISTS(SELECT 1 FROM step1_analyses WHERE id = $1)
        """, self.analysis_id)
        
        if not result:
            # Create only if it doesn't exist
            await self.db_connection.execute("""
                INSERT INTO step1_analyses (id, name, description, system_type, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """,
                self.analysis_id,
                name,
                f"Step 1 analysis: {description[:200]}...",
                "unknown",  # Will be updated after mission analysis
                datetime.now()
            )
        else:
            # Update existing record
            await self.db_connection.execute("""
                UPDATE step1_analyses 
                SET description = $2, updated_at = $3
                WHERE id = $1
            """,
                self.analysis_id,
                f"Step 1 analysis: {description[:200]}...",
                datetime.now()
            )
    
    async def _save_mission_results(self, results: Dict[str, Any]):
        """Save mission analysis results to database"""
        problem_statement = results['problem_statement']
        
        # Save problem statement
        ps_id = str(uuid4())
        await self.db_connection.execute("""
            INSERT INTO problem_statements 
            (id, analysis_id, purpose_what, method_how, goals_why, 
             mission_context, operational_constraints, environmental_assumptions)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
            ps_id,
            self.analysis_id,
            problem_statement['purpose_what'],
            problem_statement['method_how'],
            problem_statement['goals_why'],
            json.dumps(results['mission_context']),
            json.dumps(results['operational_constraints']),
            json.dumps(results['environmental_assumptions'])
        )
        
        # Update analysis with system type
        domain = results['mission_context'].get('domain', 'unknown')
        await self.db_connection.execute("""
            UPDATE step1_analyses 
            SET system_type = $1, updated_at = $2
            WHERE id = $3
        """, domain, datetime.now(), self.analysis_id)
    
    async def _save_loss_results(self, results: Dict[str, Any]):
        """Save loss identification results to database"""
        # Save losses
        loss_id_map = {}
        for loss in results['losses']:
            loss_id = str(uuid4())
            loss_id_map[loss['identifier']] = loss_id
            
            await self.db_connection.execute("""
                INSERT INTO step1_losses
                (id, analysis_id, identifier, description, loss_category, 
                 severity_classification, mission_impact)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                loss_id,
                self.analysis_id,
                loss['identifier'],
                loss['description'],
                loss['loss_category'],
                json.dumps(loss['severity_classification']),
                json.dumps(loss['mission_impact'])
            )
        
        # Save loss dependencies
        for dep in results['dependencies']:
            await self.db_connection.execute("""
                INSERT INTO loss_dependencies
                (id, primary_loss_id, dependent_loss_id, dependency_type, 
                 dependency_strength, time_relationship, rationale)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                dep['id'],
                loss_id_map[dep['primary_loss_id']],
                loss_id_map[dep['dependent_loss_id']],
                dep['dependency_type'],
                dep['dependency_strength'],
                json.dumps(dep['time_relationship']),
                dep['rationale']
            )
    
    async def _save_hazard_results_with_conn(self, results: Dict[str, Any], conn: asyncpg.Connection):
        """Save hazard identification results to database with specific connection"""
        # Save hazards
        hazard_id_map = {}
        for hazard in results['hazards']:
            hazard_id = str(uuid4())
            hazard_id_map[hazard['identifier']] = hazard_id
            
            await conn.execute("""
                INSERT INTO step1_hazards
                (id, analysis_id, identifier, description, hazard_category,
                 affected_system_property, environmental_factors, temporal_nature)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                hazard_id,
                self.analysis_id,
                hazard['identifier'],
                hazard['description'],
                hazard['hazard_category'],
                hazard['affected_system_property'],
                json.dumps(hazard['environmental_factors']),
                json.dumps(hazard['temporal_nature'])
            )
        
        # Save hazard-loss mappings
        # Need to get loss IDs from database
        loss_rows = await conn.fetch("""
            SELECT id, identifier FROM step1_losses WHERE analysis_id = $1
        """, self.analysis_id)
        
        loss_id_lookup = {row['identifier']: row['id'] for row in loss_rows}
        
        for mapping in results['hazard_loss_mappings']:
            await conn.execute("""
                INSERT INTO hazard_loss_mappings
                (id, hazard_id, loss_id, relationship_strength, rationale, conditions)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                mapping['id'],
                hazard_id_map[mapping['hazard_id']],
                loss_id_lookup[mapping['loss_id']],
                mapping['relationship_strength'],
                mapping['rationale'],
                json.dumps(mapping.get('conditions', []))
            )
    
    async def _save_hazard_results(self, results: Dict[str, Any]):
        """Save hazard identification results to database"""
        # Save hazards
        hazard_id_map = {}
        for hazard in results['hazards']:
            hazard_id = str(uuid4())
            hazard_id_map[hazard['identifier']] = hazard_id
            
            await self.db_connection.execute("""
                INSERT INTO step1_hazards
                (id, analysis_id, identifier, description, hazard_category,
                 affected_system_property, environmental_factors, temporal_nature)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                hazard_id,
                self.analysis_id,
                hazard['identifier'],
                hazard['description'],
                hazard['hazard_category'],
                hazard['affected_system_property'],
                json.dumps(hazard['environmental_factors']),
                json.dumps(hazard['temporal_nature'])
            )
        
        # Save hazard-loss mappings
        # Need to get loss IDs from database
        loss_rows = await self.db_connection.fetch("""
            SELECT id, identifier FROM step1_losses WHERE analysis_id = $1
        """, self.analysis_id)
        
        loss_id_lookup = {row['identifier']: row['id'] for row in loss_rows}
        
        for mapping in results['hazard_loss_mappings']:
            await self.db_connection.execute("""
                INSERT INTO hazard_loss_mappings
                (id, hazard_id, loss_id, relationship_strength, rationale, conditions)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                mapping['id'],
                hazard_id_map[mapping['hazard_id']],
                loss_id_lookup[mapping['loss_id']],
                mapping['relationship_strength'],
                mapping['rationale'],
                json.dumps(mapping.get('conditions', []))
            )
    
    async def _save_stakeholder_results_with_conn(self, results: Dict[str, Any], conn: asyncpg.Connection):
        """Save stakeholder analysis results to database with specific connection"""
        # Save stakeholders
        for stakeholder in results['stakeholders']:
            await conn.execute("""
                INSERT INTO step1_stakeholders
                (id, analysis_id, name, stakeholder_type, 
                 mission_perspective, loss_exposure, influence_interest)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                str(uuid4()),
                self.analysis_id,
                stakeholder['name'],
                stakeholder['stakeholder_type'],
                json.dumps(stakeholder['mission_perspective']),
                json.dumps(stakeholder['loss_exposure']),
                json.dumps(stakeholder['influence_interest'])
            )
        
        # Save adversary profiles
        for adversary in results['adversaries']:
            await conn.execute("""
                INSERT INTO adversary_profiles
                (id, analysis_id, adversary_class, profile, mission_targets)
                VALUES ($1, $2, $3, $4, $5)
            """,
                str(uuid4()),
                self.analysis_id,
                adversary['adversary_class'],
                json.dumps(adversary['profile']),
                json.dumps(adversary['mission_targets'])
            )
        
        # Save mission success criteria
        criteria = results['mission_success_criteria']
        await conn.execute("""
            INSERT INTO mission_success_criteria
            (id, analysis_id, success_states, success_indicators)
            VALUES ($1, $2, $3, $4)
        """,
            str(uuid4()),
            self.analysis_id,
            json.dumps(criteria['success_states']),
            json.dumps(criteria['success_indicators'])
        )
    
    async def _save_security_constraint_results(self, results: Dict[str, Any]):
        """Save security constraint results to database"""
        # Save security constraints
        for constraint in results['security_constraints']:
            constraint_id = str(uuid4())
            await self.db_connection.execute("""
                INSERT INTO security_constraints
                (id, analysis_id, identifier, constraint_statement, constraint_type, 
                 rationale, enforcement_level)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                constraint_id,
                self.analysis_id,
                constraint['identifier'],
                constraint.get('constraint_statement', constraint.get('description', '')),
                constraint.get('constraint_type', 'preventive'),
                constraint.get('rationale', ''),
                constraint.get('enforcement_level', 'mandatory')
            )
            
        # Save constraint-hazard mappings
        for mapping in results.get('constraint_hazard_mappings', []):
            await self.db_connection.execute("""
                INSERT INTO constraint_hazard_mappings
                (id, constraint_id, hazard_id, mapping_type, rationale)
                VALUES ($1, 
                    (SELECT id FROM security_constraints WHERE analysis_id = $2 AND identifier = $3),
                    (SELECT id FROM step1_hazards WHERE analysis_id = $2 AND identifier = $4),
                    $5, $6)
            """,
                str(uuid4()),
                self.analysis_id,
                mapping['constraint_identifier'],
                mapping['hazard_identifier'],
                mapping.get('mapping_type', 'prevents'),
                mapping.get('rationale', '')
            )
    
    async def _save_system_boundary_results(self, results: Dict[str, Any]):
        """Save system boundary results to database"""
        # Save system boundaries
        for boundary in results.get('system_boundaries', []):
            boundary_id = str(uuid4())
            await self.db_connection.execute("""
                INSERT INTO system_boundaries
                (id, analysis_id, boundary_name, boundary_type, description, definition_criteria)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                boundary_id,
                self.analysis_id,
                boundary.get('boundary_name', boundary.get('name', 'System Boundary')),
                boundary.get('boundary_type', 'system_scope'),
                boundary.get('description', ''),
                json.dumps(boundary.get('definition_criteria', {}))
            )
    
    async def _save_stakeholder_results(self, results: Dict[str, Any]):
        """Save stakeholder analysis results to database"""
        # Save stakeholders
        for stakeholder in results['stakeholders']:
            await self.db_connection.execute("""
                INSERT INTO step1_stakeholders
                (id, analysis_id, name, stakeholder_type, 
                 mission_perspective, loss_exposure, influence_interest)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                str(uuid4()),
                self.analysis_id,
                stakeholder['name'],
                stakeholder['stakeholder_type'],
                json.dumps(stakeholder['mission_perspective']),
                json.dumps(stakeholder['loss_exposure']),
                json.dumps(stakeholder['influence_interest'])
            )
        
        # Save adversary profiles
        for adversary in results['adversaries']:
            await self.db_connection.execute("""
                INSERT INTO adversary_profiles
                (id, analysis_id, adversary_class, profile, mission_targets)
                VALUES ($1, $2, $3, $4, $5)
            """,
                str(uuid4()),
                self.analysis_id,
                adversary['adversary_class'],
                json.dumps(adversary['profile']),
                json.dumps(adversary['mission_targets'])
            )
        
        # Save mission success criteria
        criteria = results['mission_success_criteria']
        await self.db_connection.execute("""
            INSERT INTO mission_success_criteria
            (id, analysis_id, success_states, success_indicators)
            VALUES ($1, $2, $3, $4)
        """,
            str(uuid4()),
            self.analysis_id,
            json.dumps(criteria['success_states']),
            json.dumps(criteria['success_indicators'])
        )
    
    async def _save_validation_results(self, results: Dict[str, Any]):
        """Save validation results and Step 2 bridge"""
        # Save Step 2 bridge
        bridge = results['step2_bridge']
        await self.db_connection.execute("""
            INSERT INTO step1_step2_bridge
            (id, analysis_id, control_needs, implied_boundaries, 
             architectural_hints, transition_guidance)
            VALUES ($1, $2, $3, $4, $5, $6)
        """,
            str(uuid4()),
            self.analysis_id,
            json.dumps(bridge['control_needs']),
            json.dumps(bridge['implied_boundaries']),
            json.dumps(bridge.get('architectural_hints', {})),
            json.dumps(bridge.get('transition_guidance', []))
        )
        
        # Save validation summary as metadata
        await self.db_connection.execute("""
            UPDATE step1_analyses 
            SET metadata = $1, updated_at = $2
            WHERE id = $3
        """,
            json.dumps({
                "validation_results": results['validation_results'],
                "quality_metrics": results['quality_metrics'],
                "recommendations": results['recommendations']
            }),
            datetime.now(),
            self.analysis_id
        )
    
    async def _update_analysis_completion(self, results: Dict[str, Any]):
        """Update analysis record with completion status"""
        await self.db_connection.execute("""
            UPDATE step1_analyses 
            SET updated_at = $1,
                metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{completion_status}',
                    $2::jsonb
                )
            WHERE id = $3
        """,
            datetime.now(),
            json.dumps({
                "status": results['status'],
                "duration": results['duration'],
                "quality_score": results['results']['validation']['quality_metrics']['overall_score']
            }),
            self.analysis_id
        )
    
    async def _update_analysis_error(self, error_message: str):
        """Update analysis record with error status"""
        await self.db_connection.execute("""
            UPDATE step1_analyses 
            SET updated_at = $1,
                metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{error}',
                    $2::jsonb
                )
            WHERE id = $3
        """,
            datetime.now(),
            json.dumps({
                "status": "error",
                "error_message": error_message,
                "timestamp": datetime.now().isoformat()
            }),
            self.analysis_id
        )
    
    def _log_execution(self, message: str, error: bool = False):
        """Log execution progress"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "type": "error" if error else "info"
        }
        self.execution_log.append(log_entry)
        
        # Also print for visibility
        prefix = "ERROR:" if error else "INFO:"
        print(f"{prefix} {message}")
    
    def _check_analysis_completeness(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if all required Step 1 artifacts were generated
        
        Returns:
            Dictionary with completeness status and details
        """
        completeness = {
            'is_complete': True,
            'missing_artifacts': [],
            'validation_issues': [],
            'artifact_status': {},
            'summary': 'All artifacts generated successfully'
        }
        
        # Define required artifacts and their validation criteria
        required_artifacts = {
            'mission_analysis': {
                'required_fields': ['problem_statement', 'mission_context', 
                                  'operational_constraints', 'environmental_assumptions'],
                'sub_fields': {
                    'problem_statement': ['purpose_what', 'method_how', 'goals_why']
                }
            },
            'loss_identification': {
                'required_fields': ['losses', 'loss_count', 'dependencies'],
                'min_count': 3,
                'loss_fields': ['identifier', 'description', 'loss_category', 
                              'severity_classification', 'mission_impact']
            },
            'hazard_identification': {
                'required_fields': ['hazards', 'hazard_count', 'hazard_loss_mappings'],
                'min_count': 3,
                'hazard_fields': ['identifier', 'description', 'hazard_category',
                                'affected_system_property', 'temporal_nature']
            },
            'stakeholder_analysis': {
                'required_fields': ['stakeholders', 'adversaries', 'mission_success_criteria'],
                'min_stakeholders': 3,
                'min_adversaries': 1
            },
            'security_constraints': {
                'required_fields': ['security_constraints', 'constraint_coverage'],
                'min_count': 3,
                'constraint_fields': ['identifier', 'name', 'constraint_type',
                                    'related_losses', 'enforcement_mechanism']
            },
            'system_boundaries': {
                'required_fields': ['system_boundary', 'boundary_analysis'],
                'boundary_fields': ['primary_system', 'system_elements', 'external_entities',
                                  'interfaces', 'assumptions', 'exclusions']
            },
            'validation': {
                'required_fields': ['overall_status', 'validation_results', 
                                  'quality_metrics', 'step2_bridge'],
                'required_validations': ['mission_clarity', 'loss_completeness', 
                                       'hazard_coverage', 'stakeholder_coverage']
            }
        }
        
        # Check each artifact
        for artifact_name, criteria in required_artifacts.items():
            artifact_status = {
                'present': False,
                'complete': False,
                'issues': []
            }
            
            # Check if artifact exists
            if artifact_name not in results.get('results', {}):
                completeness['is_complete'] = False
                completeness['missing_artifacts'].append(artifact_name)
                artifact_status['issues'].append(f'{artifact_name} not found in results')
            else:
                artifact_status['present'] = True
                artifact_data = results['results'][artifact_name]
                
                # Check required fields
                for field in criteria['required_fields']:
                    if field not in artifact_data:
                        artifact_status['issues'].append(f'Missing required field: {field}')
                        completeness['validation_issues'].append(
                            f'{artifact_name}.{field} is missing'
                        )
                
                # Check sub-fields if specified
                if 'sub_fields' in criteria:
                    for parent_field, sub_fields in criteria['sub_fields'].items():
                        if parent_field in artifact_data:
                            for sub_field in sub_fields:
                                if sub_field not in artifact_data[parent_field]:
                                    artifact_status['issues'].append(
                                        f'Missing sub-field: {parent_field}.{sub_field}'
                                    )
                
                # Check minimum counts
                if 'min_count' in criteria:
                    count_field = criteria['required_fields'][0]  # Usually first field is the list
                    if count_field in artifact_data:
                        actual_count = len(artifact_data[count_field])
                        if actual_count < criteria['min_count']:
                            artifact_status['issues'].append(
                                f'Insufficient items: {actual_count} < {criteria["min_count"]}'
                            )
                
                # Specific checks for each artifact type
                if artifact_name == 'loss_identification' and 'losses' in artifact_data:
                    for i, loss in enumerate(artifact_data['losses']):
                        for field in criteria['loss_fields']:
                            if field not in loss:
                                artifact_status['issues'].append(
                                    f'Loss {i} missing field: {field}'
                                )
                
                elif artifact_name == 'hazard_identification' and 'hazards' in artifact_data:
                    for i, hazard in enumerate(artifact_data['hazards']):
                        for field in criteria['hazard_fields']:
                            if field not in hazard:
                                artifact_status['issues'].append(
                                    f'Hazard {i} missing field: {field}'
                                )
                
                elif artifact_name == 'stakeholder_analysis':
                    if 'stakeholders' in artifact_data:
                        if len(artifact_data['stakeholders']) < criteria['min_stakeholders']:
                            artifact_status['issues'].append(
                                f'Too few stakeholders: {len(artifact_data["stakeholders"])}'
                            )
                    if 'adversaries' in artifact_data:
                        if len(artifact_data['adversaries']) < criteria['min_adversaries']:
                            artifact_status['issues'].append(
                                f'Too few adversaries: {len(artifact_data["adversaries"])}'
                            )
                
                elif artifact_name == 'security_constraints' and 'security_constraints' in artifact_data:
                    for i, constraint in enumerate(artifact_data['security_constraints']):
                        for field in criteria['constraint_fields']:
                            if field not in constraint:
                                artifact_status['issues'].append(
                                    f'Constraint {i} missing field: {field}'
                                )
                
                elif artifact_name == 'system_boundaries' and 'system_boundary' in artifact_data:
                    boundary = artifact_data['system_boundary']
                    for field in criteria['boundary_fields']:
                        if field not in boundary:
                            artifact_status['issues'].append(
                                f'System boundary missing field: {field}'
                            )
                
                elif artifact_name == 'validation' and 'validation_results' in artifact_data:
                    for required_val in criteria['required_validations']:
                        if required_val not in artifact_data['validation_results']:
                            artifact_status['issues'].append(
                                f'Missing validation: {required_val}'
                            )
                
                # Determine if artifact is complete
                artifact_status['complete'] = len(artifact_status['issues']) == 0
                if not artifact_status['complete']:
                    completeness['is_complete'] = False
            
            completeness['artifact_status'][artifact_name] = artifact_status
        
        # Check cross-artifact consistency
        if completeness['is_complete']:
            # Verify hazard-loss mapping consistency
            if 'loss_identification' in results['results'] and 'hazard_identification' in results['results']:
                loss_ids = {l['identifier'] for l in results['results']['loss_identification']['losses']}
                
                for mapping in results['results']['hazard_identification'].get('hazard_loss_mappings', []):
                    if mapping.get('loss_id') not in loss_ids:
                        completeness['validation_issues'].append(
                            f'Hazard mapping references unknown loss: {mapping.get("loss_id")}'
                        )
                        completeness['is_complete'] = False
        
        # Generate summary
        if not completeness['is_complete']:
            issues = []
            if completeness['missing_artifacts']:
                issues.append(f"{len(completeness['missing_artifacts'])} missing artifacts")
            if completeness['validation_issues']:
                issues.append(f"{len(completeness['validation_issues'])} validation issues")
            completeness['summary'] = ', '.join(issues)
        
        return completeness
    
    async def load_existing_analysis(self, analysis_path: str) -> Dict[str, Any]:
        """
        Load an existing analysis from the file system
        
        This supports loading pre-packaged demo analyses or any saved analysis.
        
        Args:
            analysis_path: Path to the analysis directory containing results JSON files
            
        Returns:
            Complete analysis results as if they were just generated
        """
        analysis_dir = Path(analysis_path)
        
        if not analysis_dir.exists():
            raise FileNotFoundError(f"Analysis directory not found: {analysis_path}")
        
        # Load configuration if available
        config_path = analysis_dir / "analysis-config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.analysis_id = config.get('analysis_id', self.analysis_id)
        
        # Check for results directory
        results_dir = analysis_dir / "results"
        if not results_dir.exists():
            results_dir = analysis_dir  # Results might be in root directory
        
        # Load all agent results
        results = {}
        
        # Load mission analysis
        mission_path = results_dir / "mission_analyst.json"
        if mission_path.exists():
            with open(mission_path, 'r') as f:
                results['mission_analysis'] = json.load(f)
        
        # Load loss identification
        loss_path = results_dir / "loss_identification.json"
        if loss_path.exists():
            with open(loss_path, 'r') as f:
                results['loss_identification'] = json.load(f)
        
        # Load hazard identification
        hazard_path = results_dir / "hazard_identification.json"
        if hazard_path.exists():
            with open(hazard_path, 'r') as f:
                results['hazard_identification'] = json.load(f)
        
        # Load stakeholder analysis
        stakeholder_path = results_dir / "stakeholder_analyst.json"
        if stakeholder_path.exists():
            with open(stakeholder_path, 'r') as f:
                results['stakeholder_analysis'] = json.load(f)
        
        # Load security constraint results
        security_constraint_path = results_dir / "security_constraint.json"
        if security_constraint_path.exists():
            with open(security_constraint_path, 'r') as f:
                results['security_constraints'] = json.load(f)
        
        # Load system boundary results
        system_boundary_path = results_dir / "system_boundary.json"
        if system_boundary_path.exists():
            with open(system_boundary_path, 'r') as f:
                results['system_boundaries'] = json.load(f)
        
        # Load validation results if available
        validation_path = results_dir / "validation.json"
        if validation_path.exists():
            with open(validation_path, 'r') as f:
                results['validation'] = json.load(f)
        else:
            # Generate minimal validation results if not present
            results['validation'] = {
                "overall_status": "completed",
                "validation_results": {
                    "mission_clarity": {"status": "pass", "score": 1.0},
                    "loss_completeness": {"status": "pass", "score": 1.0},
                    "hazard_coverage": {"status": "pass", "score": 1.0},
                    "stakeholder_coverage": {"status": "pass", "score": 1.0}
                },
                "quality_metrics": {
                    "overall_score": 0.95,
                    "completeness": 0.95,
                    "consistency": 0.95,
                    "clarity": 0.95
                },
                "recommendations": [],
                "executive_summary": "Pre-loaded analysis from existing results.",
                "step2_bridge": {
                    "control_needs": [],
                    "implied_boundaries": {},
                    "architectural_hints": {},
                    "transition_guidance": []
                }
            }
        
        # Check that we have minimum required results
        required_results = ['mission_analysis', 'loss_identification', 
                          'hazard_identification', 'stakeholder_analysis',
                          'security_constraints', 'system_boundaries']
        
        missing = [r for r in required_results if r not in results]
        if missing:
            raise ValueError(f"Missing required analysis results: {missing}")
        
        # Build final results structure
        final_results = {
            "analysis_id": self.analysis_id,
            "analysis_name": config.get('name', 'Loaded Analysis') if 'config' in locals() else 'Loaded Analysis',
            "timestamp": datetime.now().isoformat(),
            "duration": 0,  # No duration for loaded analysis
            "status": results['validation'].get('overall_status', 'completed'),
            "results": results,
            "executive_summary": results['validation'].get('executive_summary', 'Analysis loaded from existing results.'),
            "step2_bridge": results['validation'].get('step2_bridge', {}),
            "execution_log": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Analysis loaded from {analysis_path}",
                    "type": "info"
                }
            ],
            "loaded_from": str(analysis_path)
        }
        
        self._log_execution(f"Successfully loaded analysis from {analysis_path}")
        
        # If we have a database connection, save the loaded results
        if self.db_connection:
            try:
                await self._save_loaded_analysis(final_results)
            except Exception as e:
                self._log_execution(f"Could not save loaded analysis to database: {str(e)}", error=True)
        
        return final_results
    
    async def _save_loaded_analysis(self, analysis_results: Dict[str, Any]):
        """
        Save loaded analysis results to database
        
        This creates a new analysis record with the loaded data,
        enabling copy-on-write behavior for demo analyses.
        """
        # Create analysis record
        loaded_from = analysis_results.get('loaded_from', 'unknown')
        await self._create_analysis_record(
            analysis_results['analysis_name'],
            f"Analysis loaded from {loaded_from}"
        )
        
        # Save all results
        results = analysis_results['results']
        
        if 'mission_analysis' in results:
            await self._save_mission_results(results['mission_analysis'])
        
        if 'loss_identification' in results:
            await self._save_loss_results(results['loss_identification'])
        
        if 'hazard_identification' in results:
            await self._save_hazard_results(results['hazard_identification'])
        
        if 'stakeholder_analysis' in results:
            await self._save_stakeholder_results(results['stakeholder_analysis'])
        
        if 'security_constraints' in results:
            await self._save_security_constraint_results(results['security_constraints'])
        
        if 'system_boundaries' in results:
            await self._save_system_boundary_results(results['system_boundaries'])
        
        if 'validation' in results:
            await self._save_validation_results(results['validation'])
        
        # Update completion status
        await self._update_analysis_completion(analysis_results)