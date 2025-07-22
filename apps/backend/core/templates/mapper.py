"""
Template Mapper
Maps agent outputs to frontend template components.
"""
from typing import Dict, Any, Union
from pydantic import BaseModel

from core.models.templates import (
    AnalysisTable, AnalysisDiagram, AnalysisText,
    AnalysisList, AnalysisChart, AnalysisSection
)


class TemplateMapper:
    """
    Maps structured agent outputs to frontend template format.
    
    Each template type has specific props expected by the frontend.
    This ensures consistency between backend outputs and frontend rendering.
    """
    
    @staticmethod
    def map_to_frontend(
        component: BaseModel
    ) -> Dict[str, Any]:
        """Map any component to frontend format"""
        
        if isinstance(component, AnalysisTable):
            return TemplateMapper._map_table(component)
        elif isinstance(component, AnalysisDiagram):
            return TemplateMapper._map_diagram(component)
        elif isinstance(component, AnalysisText):
            return TemplateMapper._map_text(component)
        elif isinstance(component, AnalysisList):
            return TemplateMapper._map_list(component)
        elif isinstance(component, AnalysisChart):
            return TemplateMapper._map_chart(component)
        elif isinstance(component, AnalysisSection):
            return TemplateMapper._map_section(component)
        else:
            # Default mapping
            return {
                "component": component.__class__.__name__,
                "props": component.dict()
            }
            
    @staticmethod
    def _map_table(table: AnalysisTable) -> Dict[str, Any]:
        """Map table to frontend format"""
        return {
            "component": "AnalysisTable",
            "props": {
                "id": table.id,
                "title": table.title,
                "columns": table.columns,
                "data": table.data,
                "sortable": getattr(table, "sortable", True),
                "filterable": getattr(table, "filterable", True),
                "pageSize": getattr(table, "page_size", 10),
                "exportFormats": ["csv", "excel", "json", "pdf"]
            }
        }
        
    @staticmethod
    def _map_diagram(diagram: AnalysisDiagram) -> Dict[str, Any]:
        """Map diagram to frontend format"""
        return {
            "component": "AnalysisDiagram",
            "props": {
                "id": diagram.id,
                "title": diagram.title,
                "type": diagram.type,
                "data": diagram.data,
                "width": getattr(diagram, "width", "100%"),
                "height": getattr(diagram, "height", 400),
                "interactive": getattr(diagram, "interactive", True),
                "exportFormats": ["png", "svg", "pdf"]
            }
        }
        
    @staticmethod
    def _map_text(text: AnalysisText) -> Dict[str, Any]:
        """Map text to frontend format"""
        return {
            "component": "AnalysisText",
            "props": {
                "id": text.id,
                "title": text.title,
                "content": text.content,
                "format": getattr(text, "format", "plain"),
                "maxLength": getattr(text, "max_length", None),
                "editable": True,
                "exportFormats": ["txt", "pdf", "html"]
            }
        }
        
    @staticmethod
    def _map_list(list_component: AnalysisList) -> Dict[str, Any]:
        """Map list to frontend format"""
        return {
            "component": "AnalysisList",
            "props": {
                "id": list_component.id,
                "title": list_component.title,
                "items": list_component.items,
                "ordered": getattr(list_component, "ordered", False),
                "collapsible": getattr(list_component, "collapsible", True),
                "editable": True
            }
        }
        
    @staticmethod
    def _map_chart(chart: AnalysisChart) -> Dict[str, Any]:
        """Map chart to frontend format"""
        chart_type = chart.chart_type
        
        # Map to specific chart component
        component_map = {
            "bar": "AnalysisBarChart",
            "heatmap": "AnalysisHeatMap",
            "line": "AnalysisChart",
            "pie": "AnalysisChart"
        }
        
        return {
            "component": component_map.get(chart_type, "AnalysisChart"),
            "props": {
                "id": chart.id,
                "title": chart.title,
                "data": chart.data,
                "options": getattr(chart, "options", {}),
                "width": getattr(chart, "width", "100%"),
                "height": getattr(chart, "height", 400),
                "exportFormats": ["png", "svg", "pdf"]
            }
        }
        
    @staticmethod
    def _map_section(section: AnalysisSection) -> Dict[str, Any]:
        """Map section to frontend format"""
        mapped = {
            "component": "AnalysisSection",
            "props": {
                "id": section.id,
                "title": section.title,
                "level": section.level,
                "collapsible": getattr(section, "collapsible", True),
                "defaultCollapsed": getattr(section, "default_collapsed", False)
            }
        }
        
        # Map content if present
        if section.content:
            mapped["props"]["content"] = TemplateMapper.map_to_frontend(
                section.content
            )
            
        # Map subsections recursively
        if section.subsections:
            mapped["props"]["subsections"] = [
                TemplateMapper.map_to_frontend(sub)
                for sub in section.subsections
            ]
            
        return mapped
        