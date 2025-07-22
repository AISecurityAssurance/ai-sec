"""
STPA-Sec Agent Implementation
This is a critical agent as it defines the system structure used by other analyses.
"""
from typing import List, Dict, Any
from pydantic import BaseModel

from core.agents.base import BaseAnalysisAgent, AnalysisContext
from core.models.templates import (
    AnalysisSection, AnalysisTable, AnalysisDiagram,
    AnalysisText, SystemDescriptionTemplate
)


# STPA-Sec specific models
class Loss(BaseModel):
    id: str
    description: str
    stakeholders: List[str]
    severity: str  # critical, high, medium, low
    

class Hazard(BaseModel):
    id: str
    description: str
    linked_losses: List[str]
    system_state: str
    

class ControlStructure(BaseModel):
    components: List[Dict[str, Any]]
    control_actions: List[Dict[str, Any]]
    feedback_loops: List[Dict[str, Any]]
    

class UnsafeControlAction(BaseModel):
    id: str
    control_action: str
    type: str  # not-provided, provided, too-early/late, too-long/short
    context: str
    linked_hazards: List[str]
    

class CausalScenario(BaseModel):
    id: str
    uca_id: str
    description: str
    causal_factors: List[str]
    mitigations: List[str]


class StpaSecAgent(BaseAnalysisAgent):
    """
    STPA-Sec Analysis Agent
    
    Implements:
    1. Step 1: Define losses, hazards, and system constraints
    2. Step 2: Model control structure
    3. Step 3: Identify unsafe control actions
    4. Step 4: Identify causal scenarios
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__("stpa-sec", *args, **kwargs)
        
    async def analyze(self, context: AnalysisContext) -> AnalysisSection:
        """Run complete STPA-Sec analysis"""
        # Create main section
        main_section = AnalysisSection(
            id="stpa-sec-main",
            title="STPA-Sec Security Analysis",
            level=1,
            subsections=[]
        )
        
        # Step 1: System Definition
        step1 = await self._analyze_step1(context)
        main_section.subsections.append(step1)
        
        # Step 2: Control Structure
        step2 = await self._analyze_step2(context, step1)
        main_section.subsections.append(step2)
        
        # Step 3: Unsafe Control Actions
        step3 = await self._analyze_step3(context, step2)
        main_section.subsections.append(step3)
        
        # Step 4: Causal Scenarios
        step4 = await self._analyze_step4(context, step3)
        main_section.subsections.append(step4)
        
        return main_section
        
    async def _analyze_step1(
        self,
        context: AnalysisContext
    ) -> AnalysisSection:
        """Step 1: Define losses, hazards, and constraints"""
        
        # Get prompt for step 1
        prompt = self.prompts.get_prompt("stpa-sec", "step-1")
        
        # Use SystemDescriptionTemplate for structured input
        system_desc = await self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": prompt
            }, {
                "role": "user",
                "content": context.system_description
            }],
            response_model=SystemDescriptionTemplate
        )
        
        # Get losses
        losses = await self._identify_losses(context, system_desc)
        
        # Get hazards
        hazards = await self._identify_hazards(context, losses)
        
        # Create section with subsections
        section = AnalysisSection(
            id="stpa-sec-step1",
            title="Step 1: System Definition",
            level=2,
            subsections=[
                # System description
                AnalysisSection(
                    id="stpa-sec-system-desc",
                    title="System Description",
                    level=3,
                    content=system_desc
                ),
                # Losses table
                AnalysisSection(
                    id="stpa-sec-losses",
                    title="Identified Losses",
                    level=3,
                    content=AnalysisTable(
                        id="stpa-sec-losses-table",
                        title="Security Losses",
                        columns=[
                            {"key": "id", "label": "ID", "sortable": True},
                            {"key": "description", "label": "Loss Description"},
                            {"key": "stakeholders", "label": "Affected Stakeholders"},
                            {"key": "severity", "label": "Severity", 
                             "type": "dropdown",
                             "options": ["critical", "high", "medium", "low"]}
                        ],
                        data=[loss.dict() for loss in losses]
                    )
                ),
                # Hazards table
                AnalysisSection(
                    id="stpa-sec-hazards",
                    title="System Hazards",
                    level=3,
                    content=AnalysisTable(
                        id="stpa-sec-hazards-table",
                        title="Security Hazards",
                        columns=[
                            {"key": "id", "label": "ID", "sortable": True},
                            {"key": "description", "label": "Hazard Description"},
                            {"key": "linked_losses", "label": "Linked Losses"},
                            {"key": "system_state", "label": "System State"}
                        ],
                        data=[hazard.dict() for hazard in hazards]
                    )
                )
            ]
        )
        
        return section
        
    async def _analyze_step2(
        self,
        context: AnalysisContext,
        step1_results: AnalysisSection
    ) -> AnalysisSection:
        """Step 2: Model control structure"""
        
        # Extract system components from step 1
        system_info = self._extract_system_info(step1_results)
        
        # Get control structure
        control_structure = await self._model_control_structure(
            context,
            system_info
        )
        
        # Create control structure diagram
        diagram = AnalysisDiagram(
            id="stpa-sec-control-structure",
            title="System Control Structure",
            type="control-flow",
            data={
                "nodes": control_structure.components,
                "edges": control_structure.control_actions + 
                        control_structure.feedback_loops
            }
        )
        
        return AnalysisSection(
            id="stpa-sec-step2",
            title="Step 2: Control Structure",
            level=2,
            content=diagram
        )
        
    async def _analyze_step3(
        self,
        context: AnalysisContext,
        step2_results: AnalysisSection
    ) -> AnalysisSection:
        """Step 3: Identify unsafe control actions"""
        
        # Extract control actions from step 2
        control_actions = self._extract_control_actions(step2_results)
        
        # Identify UCAs for each control action
        ucas = []
        for ca in control_actions:
            uca_set = await self._identify_ucas(context, ca)
            ucas.extend(uca_set)
            
        # Create UCA table
        uca_table = AnalysisTable(
            id="stpa-sec-ucas-table",
            title="Unsafe Control Actions",
            columns=[
                {"key": "id", "label": "UCA ID", "sortable": True},
                {"key": "control_action", "label": "Control Action"},
                {"key": "type", "label": "Type", "type": "dropdown",
                 "options": ["not-provided", "provided", 
                           "too-early-late", "too-long-short"]},
                {"key": "context", "label": "Context"},
                {"key": "linked_hazards", "label": "Linked Hazards"}
            ],
            data=[uca.dict() for uca in ucas]
        )
        
        return AnalysisSection(
            id="stpa-sec-step3",
            title="Step 3: Unsafe Control Actions",
            level=2,
            content=uca_table
        )
        
    async def _analyze_step4(
        self,
        context: AnalysisContext,
        step3_results: AnalysisSection
    ) -> AnalysisSection:
        """Step 4: Identify causal scenarios"""
        
        # Extract UCAs from step 3
        ucas = self._extract_ucas(step3_results)
        
        # Generate causal scenarios
        scenarios = []
        for uca in ucas:
            scenario_set = await self._identify_scenarios(context, uca)
            scenarios.extend(scenario_set)
            
        # Create scenarios table
        scenarios_table = AnalysisTable(
            id="stpa-sec-scenarios-table",
            title="Causal Scenarios",
            columns=[
                {"key": "id", "label": "Scenario ID", "sortable": True},
                {"key": "uca_id", "label": "Related UCA"},
                {"key": "description", "label": "Scenario Description"},
                {"key": "causal_factors", "label": "Causal Factors"},
                {"key": "mitigations", "label": "Proposed Mitigations"}
            ],
            data=[scenario.dict() for scenario in scenarios]
        )
        
        return AnalysisSection(
            id="stpa-sec-step4",
            title="Step 4: Causal Scenarios",
            level=2,
            content=scenarios_table
        )
        
    def get_sections(self) -> List[str]:
        """Return list of sections"""
        return ["step1", "step2", "step3", "step4"]
        
    def get_template_structure(self) -> Dict[str, Any]:
        """Return expected template structure"""
        return {
            "step1": {
                "system_description": "SystemDescriptionTemplate",
                "losses": "AnalysisTable",
                "hazards": "AnalysisTable"
            },
            "step2": {
                "control_structure": "AnalysisDiagram"
            },
            "step3": {
                "ucas": "AnalysisTable"
            },
            "step4": {
                "scenarios": "AnalysisTable"
            }
        }
    
    # Helper methods would go here...