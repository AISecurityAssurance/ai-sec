"""Database compatibility layer for Step 2 agents."""

import logging
from typing import Dict, Any, Optional
import asyncpg
import json

logger = logging.getLogger(__name__)


class Step2DBCompat:
    """Provides backward-compatible database operations for Step 2."""
    
    def __init__(self, db_connection: asyncpg.Connection):
        self.db_connection = db_connection
        self._has_identifier_column = None
        
    async def check_identifier_column(self) -> bool:
        """Check if system_components has identifier column."""
        if self._has_identifier_column is not None:
            return self._has_identifier_column
            
        try:
            await self.db_connection.fetchval(
                "SELECT identifier FROM system_components LIMIT 1"
            )
            self._has_identifier_column = True
        except Exception as e:
            if "column" in str(e) and "identifier" in str(e):
                logger.warning("system_components table missing identifier column - using compatibility mode")
                self._has_identifier_column = False
            else:
                # Some other error - re-raise
                raise
                
        return self._has_identifier_column
        
    async def insert_component(self, component_id: str, analysis_id: str, 
                             identifier: str, name: str, component_type: str,
                             description: str, abstraction_level: str, 
                             source: str, metadata: Dict[str, Any]) -> None:
        """Insert a component with compatibility for old schema."""
        has_identifier = await self.check_identifier_column()
        
        if has_identifier:
            # New schema with identifier
            # First check if component already exists
            existing = await self.db_connection.fetchrow(
                """
                SELECT id FROM system_components 
                WHERE analysis_id = $1 AND identifier = $2
                """,
                analysis_id, identifier
            )
            
            if existing:
                # Update existing component
                await self.db_connection.execute(
                    """
                    UPDATE system_components 
                    SET name = $3, component_type = $4, description = $5,
                        abstraction_level = $6, source = $7, metadata = $8
                    WHERE id = $1 AND analysis_id = $2
                    """,
                    existing['id'], analysis_id, name, component_type,
                    description, abstraction_level, source, json.dumps(metadata)
                )
            else:
                # Insert new component
                await self.db_connection.execute(
                    """
                    INSERT INTO system_components 
                    (id, analysis_id, identifier, name, component_type, description, 
                     abstraction_level, source, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    component_id, analysis_id, identifier, name, component_type,
                    description, abstraction_level, source, json.dumps(metadata)
                )
        else:
            # Old schema without identifier - store it in metadata
            metadata['identifier'] = identifier
            await self.db_connection.execute(
                """
                INSERT INTO system_components 
                (id, analysis_id, name, component_type, description, 
                 abstraction_level, source, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                component_id, analysis_id, name, component_type,
                description, abstraction_level, source, json.dumps(metadata)
            )
            
    async def insert_control_action(self, action_id: str, analysis_id: str,
                                  identifier: str, controller_id: str,
                                  controlled_process_id: str, action_name: str,
                                  action_description: str, action_type: Optional[str],
                                  timing_requirements: Optional[Dict],
                                  authority_level: Optional[str]) -> None:
        """Insert a control action with compatibility."""
        has_identifier = await self.check_identifier_column()
        
        if has_identifier:
            # Check if action already exists
            existing = await self.db_connection.fetchrow(
                """
                SELECT id FROM control_actions 
                WHERE analysis_id = $1 AND identifier = $2
                """,
                analysis_id, identifier
            )
            
            if existing:
                # Update existing action
                await self.db_connection.execute(
                    """
                    UPDATE control_actions 
                    SET controller_id = $3, controlled_process_id = $4,
                        action_name = $5, action_description = $6, action_type = $7,
                        timing_requirements = $8, authority_level = $9
                    WHERE id = $1 AND analysis_id = $2
                    """,
                    existing['id'], analysis_id, controller_id, controlled_process_id,
                    action_name, action_description, action_type,
                    json.dumps(timing_requirements) if timing_requirements else None,
                    authority_level
                )
            else:
                # Insert new action
                await self.db_connection.execute(
                    """
                    INSERT INTO control_actions 
                    (id, analysis_id, identifier, controller_id, controlled_process_id,
                     action_name, action_description, action_type, timing_requirements,
                     authority_level)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    action_id, analysis_id, identifier, controller_id, controlled_process_id,
                    action_name, action_description, action_type,
                    json.dumps(timing_requirements) if timing_requirements else None,
                    authority_level
                )
        else:
            # Old schema - skip identifier
            await self.db_connection.execute(
                """
                INSERT INTO control_actions 
                (id, analysis_id, controller_id, controlled_process_id,
                 action_name, action_description, action_type, timing_requirements,
                 authority_level)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                action_id, analysis_id, controller_id, controlled_process_id,
                action_name, action_description, action_type,
                json.dumps(timing_requirements) if timing_requirements else None,
                authority_level
            )
            
    async def insert_feedback_mechanism(self, feedback_id: str, analysis_id: str,
                                      identifier: str, source_process_id: str,
                                      target_controller_id: str, feedback_name: str,
                                      information_type: str, information_content: str,
                                      timing_characteristics: Optional[Dict],
                                      reliability_requirements: Optional[Dict]) -> None:
        """Insert a feedback mechanism with compatibility."""
        has_identifier = await self.check_identifier_column()
        
        if has_identifier:
            await self.db_connection.execute(
                """
                INSERT INTO feedback_mechanisms 
                (id, analysis_id, identifier, source_process_id, target_controller_id,
                 feedback_name, information_type, information_content,
                 timing_characteristics, reliability_requirements)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                feedback_id, analysis_id, identifier, source_process_id,
                target_controller_id, feedback_name, information_type,
                information_content,
                json.dumps(timing_characteristics) if timing_characteristics else None,
                json.dumps(reliability_requirements) if reliability_requirements else None
            )
        else:
            # Old schema - skip identifier
            await self.db_connection.execute(
                """
                INSERT INTO feedback_mechanisms 
                (id, analysis_id, source_process_id, target_controller_id,
                 feedback_name, information_type, information_content,
                 timing_characteristics, reliability_requirements)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                feedback_id, analysis_id, source_process_id,
                target_controller_id, feedback_name, information_type,
                information_content,
                json.dumps(timing_characteristics) if timing_characteristics else None,
                json.dumps(reliability_requirements) if reliability_requirements else None
            )
            
    async def insert_trust_boundary(self, boundary_id: str, analysis_id: str,
                                  identifier: str, boundary_name: str,
                                  boundary_type: Optional[str], component_a_id: str,
                                  component_b_id: str, trust_direction: str,
                                  authentication_method: Optional[str],
                                  authorization_method: Optional[str],
                                  data_protection_requirements: Optional[Dict]) -> None:
        """Insert a trust boundary with compatibility."""
        has_identifier = await self.check_identifier_column()
        
        if has_identifier:
            await self.db_connection.execute(
                """
                INSERT INTO trust_boundaries 
                (id, analysis_id, identifier, boundary_name, boundary_type,
                 component_a_id, component_b_id, trust_direction,
                 authentication_method, authorization_method,
                 data_protection_requirements)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                boundary_id, analysis_id, identifier, boundary_name, boundary_type,
                component_a_id, component_b_id, trust_direction,
                authentication_method, authorization_method,
                json.dumps(data_protection_requirements) if data_protection_requirements else None
            )
        else:
            # Old schema - skip identifier
            await self.db_connection.execute(
                """
                INSERT INTO trust_boundaries 
                (id, analysis_id, boundary_name, boundary_type,
                 component_a_id, component_b_id, trust_direction,
                 authentication_method, authorization_method,
                 data_protection_requirements)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                boundary_id, analysis_id, boundary_name, boundary_type,
                component_a_id, component_b_id, trust_direction,
                authentication_method, authorization_method,
                json.dumps(data_protection_requirements) if data_protection_requirements else None
            )