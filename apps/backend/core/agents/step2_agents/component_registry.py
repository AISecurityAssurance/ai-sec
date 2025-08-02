"""
Component Registry for Step 2 STPA-Sec Analysis

Maintains a consistent registry of all components identified during Step 2 analysis
to ensure cross-agent consistency and prevent references to undefined components.
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Component:
    """Represents a system component in the control structure."""
    identifier: str
    name: str
    type: str  # controller, process, dual-role
    description: str
    source: str  # which agent identified it
    properties: Dict[str, Any] = field(default_factory=dict)
    references: Set[str] = field(default_factory=set)  # other components this references
    referenced_by: Set[str] = field(default_factory=set)  # components that reference this


class ComponentRegistry:
    """
    Centralized registry for all components identified during Step 2 analysis.
    Ensures consistency across agents and prevents undefined references.
    """
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.controllers: Set[str] = set()
        self.processes: Set[str] = set()
        self.dual_roles: Set[str] = set()
        self.undefined_references: Set[str] = set()
        self.validation_errors: List[str] = []
        
    def register_component(self, identifier: str, name: str, comp_type: str, 
                         description: str, source: str, **properties) -> bool:
        """
        Register a new component in the registry.
        
        Args:
            identifier: Unique identifier (e.g., CTRL-1, PROC-1)
            name: Human-readable name
            comp_type: Type of component (controller, process, dual-role)
            description: Description of the component
            source: Which agent identified this component
            **properties: Additional properties
            
        Returns:
            bool: True if registered successfully, False if already exists
        """
        if identifier in self.components:
            self.validation_errors.append(
                f"Component {identifier} already registered by {self.components[identifier].source}"
            )
            return False
            
        component = Component(
            identifier=identifier,
            name=name,
            type=comp_type,
            description=description,
            source=source,
            properties=properties
        )
        
        self.components[identifier] = component
        
        # Track by type
        if comp_type == "controller":
            self.controllers.add(identifier)
        elif comp_type == "process":
            self.processes.add(identifier)
        elif comp_type == "dual-role":
            self.dual_roles.add(identifier)
            
        return True
        
    def add_reference(self, from_component: str, to_component: str) -> bool:
        """
        Add a reference between components (e.g., control action from CTRL-1 to PROC-1).
        
        Args:
            from_component: Source component identifier
            to_component: Target component identifier
            
        Returns:
            bool: True if reference added, False if components don't exist
        """
        # Check if both components exist
        if from_component not in self.components:
            self.undefined_references.add(from_component)
            self.validation_errors.append(
                f"Reference from undefined component: {from_component}"
            )
            return False
            
        if to_component not in self.components:
            self.undefined_references.add(to_component)
            self.validation_errors.append(
                f"Reference to undefined component: {to_component}"
            )
            return False
            
        # Add the reference
        self.components[from_component].references.add(to_component)
        self.components[to_component].referenced_by.add(from_component)
        return True
        
    def validate_component_reference(self, identifier: str) -> bool:
        """Check if a component identifier exists in the registry."""
        return identifier in self.components
        
    def get_component(self, identifier: str) -> Optional[Component]:
        """Get a component by identifier."""
        return self.components.get(identifier)
        
    def get_components_by_type(self, comp_type: str) -> List[Component]:
        """Get all components of a specific type."""
        return [c for c in self.components.values() if c.type == comp_type]
        
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate a validation report for the registry.
        
        Returns:
            Dict containing validation results and statistics
        """
        orphaned_components = []
        for comp_id, comp in self.components.items():
            if not comp.references and not comp.referenced_by:
                if comp.type != "process":  # Processes might not have references
                    orphaned_components.append(comp_id)
                    
        return {
            "total_components": len(self.components),
            "controllers": len(self.controllers),
            "processes": len(self.processes),
            "dual_roles": len(self.dual_roles),
            "undefined_references": list(self.undefined_references),
            "orphaned_components": orphaned_components,
            "validation_errors": self.validation_errors,
            "is_valid": len(self.undefined_references) == 0 and len(self.validation_errors) == 0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary for serialization."""
        return {
            "components": {
                comp_id: {
                    "identifier": comp.identifier,
                    "name": comp.name,
                    "type": comp.type,
                    "description": comp.description,
                    "source": comp.source,
                    "properties": comp.properties,
                    "references": list(comp.references),
                    "referenced_by": list(comp.referenced_by)
                }
                for comp_id, comp in self.components.items()
            },
            "controllers": list(self.controllers),
            "processes": list(self.processes),
            "dual_roles": list(self.dual_roles),
            "undefined_references": list(self.undefined_references),
            "validation_errors": self.validation_errors,
            "timestamp": datetime.now().isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentRegistry':
        """Create registry from dictionary."""
        registry = cls()
        
        # Restore components
        for comp_id, comp_data in data.get("components", {}).items():
            component = Component(
                identifier=comp_data["identifier"],
                name=comp_data["name"],
                type=comp_data["type"],
                description=comp_data["description"],
                source=comp_data["source"],
                properties=comp_data.get("properties", {}),
                references=set(comp_data.get("references", [])),
                referenced_by=set(comp_data.get("referenced_by", []))
            )
            registry.components[comp_id] = component
            
        # Restore type sets
        registry.controllers = set(data.get("controllers", []))
        registry.processes = set(data.get("processes", []))
        registry.dual_roles = set(data.get("dual_roles", []))
        registry.undefined_references = set(data.get("undefined_references", []))
        registry.validation_errors = data.get("validation_errors", [])
        
        return registry
        
    def get_prompt_context(self) -> str:
        """
        Generate a context string for prompts to inform agents about existing components.
        """
        context = "## Existing Components in Control Structure\n\n"
        
        if self.controllers:
            context += "### Controllers:\n"
            for ctrl_id in sorted(self.controllers):
                comp = self.components[ctrl_id]
                context += f"- {ctrl_id}: {comp.name} - {comp.description}\n"
            context += "\n"
            
        if self.processes:
            context += "### Controlled Processes:\n"
            for proc_id in sorted(self.processes):
                comp = self.components[proc_id]
                context += f"- {proc_id}: {comp.name} - {comp.description}\n"
            context += "\n"
            
        if self.dual_roles:
            context += "### Dual-Role Components:\n"
            for dual_id in sorted(self.dual_roles):
                comp = self.components[dual_id]
                context += f"- {dual_id}: {comp.name} - {comp.description}\n"
            context += "\n"
            
        context += "**IMPORTANT**: Only reference the component identifiers listed above. "
        context += "Do NOT create new component identifiers.\n"
        
        return context