"""
Step 1 Coordinator for STPA-Sec Analysis
"""
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
from uuid import uuid4
import asyncpg

from .mission_analyst import MissionAnalystAgent
from .loss_identification import LossIdentificationAgent
from .hazard_identification import HazardIdentificationAgent
from .stakeholder_analyst import StakeholderAnalystAgent
from .validation_agent import ValidationAgent


class Step1Coordinator:
    """
    Coordinates all Step 1 agents to perform complete STPA-Sec Step 1 analysis
    
    Execution flow:
    1. Mission Analyst - Extract mission and context
    2. Loss Identification - Identify unacceptable outcomes
    3. Hazard Identification - Identify hazardous states (depends on losses)
    4. Stakeholder Analyst - Analyze perspectives (depends on losses)
    5. Validation - Validate and create Step 2 bridge
    """
    
    def __init__(self, analysis_id: Optional[str] = None, db_connection: Optional[asyncpg.Connection] = None):
        self.analysis_id = analysis_id or str(uuid4())
        self.db_connection = db_connection
        self.execution_log = []
        
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
            loss_agent = LossIdentificationAgent(self.analysis_id, self.db_connection)
            loss_results = await loss_agent.analyze(context)
            
            if self.db_connection:
                await self._save_loss_results(loss_results)
            
            # Phase 3: Parallel execution of Hazard and Stakeholder analysis
            self._log_execution("Starting Phase 3: Hazard and Stakeholder Analysis (parallel)")
            
            hazard_task = asyncio.create_task(self._run_hazard_analysis(context))
            stakeholder_task = asyncio.create_task(self._run_stakeholder_analysis(context))
            
            hazard_results, stakeholder_results = await asyncio.gather(
                hazard_task, stakeholder_task
            )
            
            # Phase 4: Validation
            self._log_execution("Starting Phase 4: Validation and Quality Assessment")
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
                    "validation": validation_results
                },
                "executive_summary": validation_results['executive_summary'],
                "step2_bridge": validation_results['step2_bridge'],
                "execution_log": self.execution_log
            }
            
            # Update analysis record with completion
            if self.db_connection:
                await self._update_analysis_completion(final_results)
            
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
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')
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
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')
        stakeholder_conn = await asyncpg.connect(DATABASE_URL)
        
        try:
            stakeholder_agent = StakeholderAnalystAgent(self.analysis_id, stakeholder_conn)
            results = await stakeholder_agent.analyze(context)
            
            # Save using the stakeholder connection, not the main one
            await self._save_stakeholder_results_with_conn(results, stakeholder_conn)
            
            return results
        finally:
            await stakeholder_conn.close()
    
    async def _create_analysis_record(self, name: str, description: str):
        """Create initial analysis record"""
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