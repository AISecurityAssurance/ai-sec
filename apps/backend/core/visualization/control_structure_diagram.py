"""
Control Structure Diagram Generator

Generates visual diagrams from Step 2 control structure analysis results.
"""
from typing import Dict, Any, List, Optional, Tuple
import json
from pathlib import Path
import logging


class ControlStructureDiagramGenerator:
    """
    Generates visual control structure diagrams in multiple formats.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_mermaid_diagram(self, synthesis: Dict[str, Any]) -> str:
        """
        Generate a Mermaid diagram from synthesis data.
        
        Returns:
            Mermaid diagram code as a string
        """
        lines = ["graph TB"]
        lines.append("    %% Control Structure Diagram")
        lines.append("    ")
        
        # Style definitions
        lines.extend([
            "    %% Style definitions",
            "    classDef controller fill:#ff9999,stroke:#333,stroke-width:2px",
            "    classDef process fill:#99ccff,stroke:#333,stroke-width:2px",
            "    classDef boundary fill:#ffffcc,stroke:#ff6666,stroke-width:3px,stroke-dasharray: 5 5",
            "    classDef feedback stroke:#00aa00,stroke-width:2px",
            "    classDef action stroke:#0066cc,stroke-width:2px",
            "    "
        ])
        
        # Get all components
        controllers = synthesis.get('all_controllers', [])
        processes = synthesis.get('all_processes', [])
        boundaries = synthesis.get('trust_boundaries', [])
        actions = synthesis.get('critical_control_actions', [])
        feedbacks = synthesis.get('key_feedback_mechanisms', [])
        
        # Add controllers
        lines.append("    %% Controllers")
        for ctrl in controllers:
            ctrl_id = ctrl['identifier']
            ctrl_name = self._escape_mermaid(ctrl['name'])
            authority = ctrl.get('authority_level', 'unknown')
            lines.append(f'    {ctrl_id}["{ctrl_name}<br/><i>{authority} authority</i>"]')
            lines.append(f'    class {ctrl_id} controller')
        lines.append("    ")
        
        # Add controlled processes
        lines.append("    %% Controlled Processes")
        for proc in processes:
            proc_id = proc['identifier']
            proc_name = self._escape_mermaid(proc['name'])
            criticality = proc.get('criticality', 'unknown')
            lines.append(f'    {proc_id}("{proc_name}<br/><i>{criticality} criticality</i>")')
            lines.append(f'    class {proc_id} process')
        lines.append("    ")
        
        # Add trust boundaries as subgraphs
        if boundaries:
            lines.append("    %% Trust Boundaries")
            for i, boundary in enumerate(boundaries):
                boundary_id = f"subgraph{i}"
                boundary_name = self._escape_mermaid(boundary['name'])
                lines.append(f'    subgraph {boundary_id} ["{boundary_name}"]')
                
                # Add components within boundary
                components = boundary.get('components', boundary.get('between', []))
                for comp in components:
                    if comp:
                        lines.append(f'        {comp}')
                lines.append('    end')
                lines.append(f'    class {boundary_id} boundary')
            lines.append("    ")
        
        # Add control actions
        lines.append("    %% Control Actions")
        for action in actions:
            from_id = action.get('from')
            to_id = action.get('to')
            action_name = self._escape_mermaid(action['name'])
            action_type = action.get('type', 'command')
            
            if from_id and to_id:
                # Check if this crosses boundaries
                crosses = action.get('crosses_boundaries', [])
                if crosses:
                    label = f"{action_name}<br/><b>[{action_type}]</b><br/><i>crosses boundary</i>"
                    lines.append(f'    {from_id} -->|"{label}"| {to_id}')
                else:
                    label = f"{action_name}<br/>[{action_type}]"
                    lines.append(f'    {from_id} -->|"{label}"| {to_id}')
        lines.append("    ")
        
        # Add feedback mechanisms
        if feedbacks:
            lines.append("    %% Feedback Mechanisms")
            for feedback in feedbacks:
                source = feedback.get('source', feedback.get('from'))
                target = feedback.get('target', feedback.get('to'))
                feedback_name = self._escape_mermaid(feedback['name'])
                feedback_type = feedback.get('type', 'status')
                
                if source and target:
                    label = f"{feedback_name}<br/>[{feedback_type}]"
                    lines.append(f'    {source} -.->|"{label}"| {target}')
            lines.append("    ")
        
        # Add legend
        lines.extend([
            "    %% Legend",
            "    subgraph Legend",
            '        L1["Controller"]',
            '        L2("Controlled Process")',
            '        L3["Trust Boundary"]:::boundary',
            "        L1 -->|Control Action| L2",
            "        L2 -.->|Feedback| L1",
            "    end",
            "    class L1 controller",
            "    class L2 process"
        ])
        
        return "\n".join(lines)
    
    def generate_graphviz_dot(self, synthesis: Dict[str, Any]) -> str:
        """
        Generate a Graphviz DOT diagram from synthesis data.
        
        Returns:
            DOT diagram code as a string
        """
        lines = ["digraph ControlStructure {"]
        lines.extend([
            '    rankdir=TB;',
            '    node [shape=box, style=filled];',
            '    edge [fontsize=10];',
            '    ',
            '    // Graph attributes',
            '    graph [label="Control Structure Diagram", fontsize=16, fontweight=bold];',
            '    '
        ])
        
        # Get all components
        controllers = synthesis.get('all_controllers', [])
        processes = synthesis.get('all_processes', [])
        boundaries = synthesis.get('trust_boundaries', [])
        actions = synthesis.get('critical_control_actions', [])
        feedbacks = synthesis.get('key_feedback_mechanisms', [])
        
        # Add controllers
        lines.append('    // Controllers')
        for ctrl in controllers:
            ctrl_id = ctrl['identifier']
            ctrl_name = self._escape_dot(ctrl['name'])
            authority = ctrl.get('authority_level', 'unknown')
            color = '#ff9999' if authority == 'high' else '#ffcccc'
            lines.append(f'    {ctrl_id} [label="{ctrl_name}\\n[{authority}]", fillcolor="{color}", shape=box];')
        lines.append('    ')
        
        # Add controlled processes
        lines.append('    // Controlled Processes')
        for proc in processes:
            proc_id = proc['identifier']
            proc_name = self._escape_dot(proc['name'])
            criticality = proc.get('criticality', 'unknown')
            color = '#6699ff' if criticality == 'high' else '#99ccff'
            lines.append(f'    {proc_id} [label="{proc_name}\\n[{criticality}]", fillcolor="{color}", shape=ellipse];')
        lines.append('    ')
        
        # Add trust boundaries as clusters
        if boundaries:
            lines.append('    // Trust Boundaries')
            for i, boundary in enumerate(boundaries):
                boundary_name = self._escape_dot(boundary['name'])
                lines.append(f'    subgraph cluster_{i} {{')
                lines.append(f'        label="{boundary_name}";')
                lines.append('        style=dashed;')
                lines.append('        color=red;')
                
                # Add components within boundary
                components = boundary.get('components', boundary.get('between', []))
                for comp in components:
                    if comp:
                        lines.append(f'        {comp};')
                lines.append('    }')
            lines.append('    ')
        
        # Add control actions
        lines.append('    // Control Actions')
        for action in actions:
            from_id = action.get('from')
            to_id = action.get('to')
            action_name = self._escape_dot(action['name'])
            action_type = action.get('type', 'command')
            
            if from_id and to_id:
                # Check if this crosses boundaries
                crosses = action.get('crosses_boundaries', [])
                if crosses:
                    lines.append(f'    {from_id} -> {to_id} [label="{action_name}\\n[{action_type}]", color=red, penwidth=2];')
                else:
                    lines.append(f'    {from_id} -> {to_id} [label="{action_name}\\n[{action_type}]", color=blue];')
        lines.append('    ')
        
        # Add feedback mechanisms
        if feedbacks:
            lines.append('    // Feedback Mechanisms')
            for feedback in feedbacks:
                source = feedback.get('source', feedback.get('from'))
                target = feedback.get('target', feedback.get('to'))
                feedback_name = self._escape_dot(feedback['name'])
                feedback_type = feedback.get('type', 'status')
                
                if source and target:
                    lines.append(f'    {source} -> {target} [label="{feedback_name}\\n[{feedback_type}]", color=green, style=dashed];')
        
        lines.append('}')
        return "\n".join(lines)
    
    def generate_plantuml_diagram(self, synthesis: Dict[str, Any]) -> str:
        """
        Generate a PlantUML diagram from synthesis data.
        
        Returns:
            PlantUML diagram code as a string
        """
        lines = ["@startuml"]
        lines.extend([
            "!theme plain",
            "title Control Structure Diagram",
            "",
            "' Component definitions",
            "skinparam component {",
            "    BackgroundColor<<Controller>> LightSalmon",
            "    BackgroundColor<<Process>> LightBlue",
            "    BorderColor Black",
            "}",
            ""
        ])
        
        # Get all components
        controllers = synthesis.get('all_controllers', [])
        processes = synthesis.get('all_processes', [])
        actions = synthesis.get('critical_control_actions', [])
        feedbacks = synthesis.get('key_feedback_mechanisms', [])
        
        # Add controllers
        lines.append("' Controllers")
        for ctrl in controllers:
            ctrl_id = ctrl['identifier']
            ctrl_name = ctrl['name']
            authority = ctrl.get('authority_level', 'unknown')
            lines.append(f'component "{ctrl_name}\\n<{authority}>" as {ctrl_id} <<Controller>>')
        lines.append("")
        
        # Add controlled processes
        lines.append("' Controlled Processes")
        for proc in processes:
            proc_id = proc['identifier']
            proc_name = proc['name']
            criticality = proc.get('criticality', 'unknown')
            lines.append(f'component "{proc_name}\\n<{criticality}>" as {proc_id} <<Process>>')
        lines.append("")
        
        # Add control actions
        lines.append("' Control Actions")
        for action in actions:
            from_id = action.get('from')
            to_id = action.get('to')
            action_name = action['name']
            
            if from_id and to_id:
                if action.get('crosses_boundaries'):
                    lines.append(f'{from_id} -[#red,bold]-> {to_id} : {action_name}')
                else:
                    lines.append(f'{from_id} -[#blue]-> {to_id} : {action_name}')
        lines.append("")
        
        # Add feedback mechanisms
        if feedbacks:
            lines.append("' Feedback Mechanisms")
            for feedback in feedbacks:
                source = feedback.get('source', feedback.get('from'))
                target = feedback.get('target', feedback.get('to'))
                feedback_name = feedback['name']
                
                if source and target:
                    lines.append(f'{source} -[#green,dashed]-> {target} : {feedback_name}')
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def save_diagrams(self, synthesis: Dict[str, Any], output_dir: Path) -> List[Path]:
        """
        Save all diagram formats to files.
        
        Returns:
            List of paths to saved diagram files
        """
        saved_files = []
        
        # Ensure output directory exists
        diagrams_dir = output_dir / "diagrams"
        diagrams_dir.mkdir(exist_ok=True)
        
        # Save Mermaid diagram
        mermaid_file = diagrams_dir / "control_structure.mmd"
        with open(mermaid_file, 'w') as f:
            f.write(self.generate_mermaid_diagram(synthesis))
        saved_files.append(mermaid_file)
        self.logger.info(f"Saved Mermaid diagram to {mermaid_file}")
        
        # Save Graphviz DOT diagram
        dot_file = diagrams_dir / "control_structure.dot"
        with open(dot_file, 'w') as f:
            f.write(self.generate_graphviz_dot(synthesis))
        saved_files.append(dot_file)
        self.logger.info(f"Saved Graphviz DOT diagram to {dot_file}")
        
        # Save PlantUML diagram
        puml_file = diagrams_dir / "control_structure.puml"
        with open(puml_file, 'w') as f:
            f.write(self.generate_plantuml_diagram(synthesis))
        saved_files.append(puml_file)
        self.logger.info(f"Saved PlantUML diagram to {puml_file}")
        
        # Save diagram metadata
        metadata = {
            "generated_at": str(Path.cwd()),
            "formats": {
                "mermaid": {
                    "file": "control_structure.mmd",
                    "viewer": "https://mermaid.live",
                    "instructions": "Copy content to Mermaid Live Editor or use in Markdown with ```mermaid blocks"
                },
                "graphviz": {
                    "file": "control_structure.dot",
                    "command": "dot -Tpng control_structure.dot -o control_structure.png",
                    "viewer": "http://www.webgraphviz.com/"
                },
                "plantuml": {
                    "file": "control_structure.puml",
                    "command": "plantuml control_structure.puml",
                    "viewer": "http://www.plantuml.com/plantuml"
                }
            }
        }
        
        metadata_file = diagrams_dir / "diagram_info.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        saved_files.append(metadata_file)
        
        return saved_files
    
    def _escape_mermaid(self, text: str) -> str:
        """Escape special characters for Mermaid."""
        return text.replace('"', '&quot;').replace('\n', '<br/>')
    
    def _escape_dot(self, text: str) -> str:
        """Escape special characters for Graphviz DOT."""
        return text.replace('"', '\\"').replace('\n', '\\n')