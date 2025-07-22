"""
Template Mapper
Maps agent outputs to frontend template components.
"""
from typing import Dict, Any, Union, List, Optional
from pydantic import BaseModel

from core.models.schemas import (
    TableColumn, TableData, ChartData, DiagramNode, DiagramEdge, DiagramData
)


class TemplateMapper:
    """
    Maps structured agent outputs to frontend template format.
    
    Each template type has specific props expected by the frontend.
    This ensures consistency between backend outputs and frontend rendering.
    """
    
    @staticmethod
    def validate_table_data(data: Dict[str, Any]) -> bool:
        """Validate table data structure"""
        try:
            TableData(**data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_chart_data(data: Dict[str, Any]) -> bool:
        """Validate chart data structure"""
        try:
            ChartData(**data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_diagram_data(data: Dict[str, Any]) -> bool:
        """Validate diagram data structure"""
        try:
            DiagramData(**data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def map_to_table(
        headers: List[str],
        rows: List[List[Any]],
        editable_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Map data to table template"""
        columns = [
            TableColumn(
                key=f"col_{i}",
                label=header,
                type="text",
                editable=header in (editable_columns or [])
            )
            for i, header in enumerate(headers)
        ]
        
        table_rows = [
            {f"col_{i}": value for i, value in enumerate(row)}
            for row in rows
        ]
        
        return {
            "template_type": "table",
            "data": TableData(
                columns=columns,
                rows=table_rows,
                editable=bool(editable_columns),
                sortable=True,
                filterable=True
            ).model_dump()
        }
    
    @staticmethod
    def map_to_bar_chart(
        labels: List[str],
        values: List[float],
        title: str = "Values",
        horizontal: bool = True,
        use_colors: bool = False,
        colors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Map data to bar chart template"""
        data_items = []
        default_colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#f39c12", 
            "#9b59b6", "#1abc9c", "#34495e", "#f1c40f"
        ]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            item = {
                "label": label,
                "value": value
            }
            if use_colors:
                if colors and i < len(colors):
                    item["color"] = colors[i]
                else:
                    item["color"] = default_colors[i % len(default_colors)]
            data_items.append(item)
        
        return {
            "template_type": "bar_chart",
            "data": {
                "data": data_items,
                "horizontal": horizontal,
                "useColors": use_colors,
                "xAxisLabel": "Value" if horizontal else None,
                "yAxisLabel": None if horizontal else "Value"
            }
        }
    
    @staticmethod
    def map_to_heat_map(
        rows: List[str],
        cols: List[str],
        cells: List[Dict[str, Any]],
        color_scale: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Map data to heat map template"""
        return {
            "template_type": "heat_map",
            "data": {
                "config": {
                    "rows": rows,
                    "cols": cols,
                    "cells": cells,
                    "colorScale": color_scale
                }
            }
        }
    
    @staticmethod
    def map_to_pie_chart(
        labels: List[str],
        values: List[float],
        colors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Map data to pie chart template"""
        default_colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#f39c12", 
            "#9b59b6", "#1abc9c", "#34495e", "#f1c40f"
        ]
        
        return {
            "template_type": "chart",
            "data": ChartData(
                type="pie",
                labels=labels,
                datasets=[{
                    "data": values,
                    "backgroundColor": colors or default_colors[:len(labels)]
                }]
            ).model_dump()
        }
    
    @staticmethod
    def map_to_flow_diagram(
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        layout: str = "hierarchical"
    ) -> Dict[str, Any]:
        """Map data to flow diagram template"""
        diagram_nodes = [
            DiagramNode(
                id=node.get("id", f"node_{i}"),
                label=node.get("label", f"Node {i}"),
                type=node.get("type", "default"),
                position=node.get("position"),
                data=node.get("data", {})
            )
            for i, node in enumerate(nodes)
        ]
        
        diagram_edges = [
            DiagramEdge(
                id=edge.get("id", f"edge_{i}"),
                source=edge["source"],
                target=edge["target"],
                label=edge.get("label"),
                type=edge.get("type", "default"),
                data=edge.get("data", {})
            )
            for i, edge in enumerate(edges)
        ]
        
        return {
            "template_type": "diagram",
            "data": DiagramData(
                nodes=diagram_nodes,
                edges=diagram_edges,
                layout=layout
            ).model_dump()
        }
    
    @staticmethod
    def map_to_text(
        content: str,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """Map content to text template"""
        return {
            "template_type": "text",
            "data": {
                "content": content,
                "format": format
            }
        }
    
    @staticmethod
    def map_to_list(
        items: List[Any],
        ordered: bool = False,
        item_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Map items to list template"""
        formatted_items = []
        
        for item in items:
            if isinstance(item, str):
                formatted_items.append({"content": item})
            elif isinstance(item, dict):
                formatted_items.append(item)
            else:
                formatted_items.append({"content": str(item)})
        
        return {
            "template_type": "list",
            "data": {
                "items": formatted_items,
                "ordered": ordered,
                "item_template": item_template
            }
        }
    
    @staticmethod
    def validate_template_data(template_type: str, data: Dict[str, Any]) -> bool:
        """Validate data matches expected template structure"""
        validators = {
            "table": TemplateMapper.validate_table_data,
            "chart": TemplateMapper.validate_chart_data,
            "diagram": TemplateMapper.validate_diagram_data,
            "text": lambda d: "content" in d and "format" in d,
            "list": lambda d: "items" in d and isinstance(d["items"], list)
        }
        
        validator = validators.get(template_type)
        if validator:
            return validator(data)
        return False


# Convenience functions for agents
def create_threat_table(
    threats: List[Dict[str, Any]],
    columns: List[str] = ["ID", "Threat", "Category", "Impact", "Likelihood", "Mitigation"]
) -> Dict[str, Any]:
    """Create a standard threat table"""
    mapper = TemplateMapper()
    rows = []
    for threat in threats:
        row = []
        for col in columns:
            key = col.lower().replace(" ", "_")
            row.append(threat.get(key, ""))
        rows.append(row)
    
    return mapper.map_to_table(columns, rows)


def create_risk_matrix(
    risks: List[Dict[str, Any]],
    impact_levels: List[str] = ["Low", "Medium", "High", "Critical"],
    likelihood_levels: List[str] = ["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]
) -> Dict[str, Any]:
    """Create a risk matrix heat map"""
    mapper = TemplateMapper()
    
    # Create cells for heat map
    cells = []
    for risk in risks:
        impact = risk.get("impact", "Medium")
        likelihood = risk.get("likelihood", "Possible")
        
        cells.append({
            "row": impact,
            "col": likelihood,
            "value": _calculate_risk_score(impact, likelihood),
            "label": risk.get("id", ""),
            "tooltip": risk.get("description", "")
        })
    
    return mapper.map_to_heat_map(
        rows=impact_levels,
        cols=likelihood_levels,
        cells=cells
    )


def _calculate_risk_score(impact: str, likelihood: str) -> int:
    """Calculate risk score based on impact and likelihood"""
    impact_scores = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    likelihood_scores = {"Rare": 1, "Unlikely": 2, "Possible": 3, "Likely": 4, "Almost Certain": 5}
    
    return impact_scores.get(impact, 2) * likelihood_scores.get(likelihood, 3)