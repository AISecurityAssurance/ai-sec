"""Unified output display system for analysis results."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class OutputDisplay:
    """Handles unified display of analysis outputs."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self._output_sections: List[Dict[str, Any]] = []
        
    def add_section(self, title: str, base_path: Path, files: List[Path], 
                   is_secondary: bool = False):
        """Add an output section to display.
        
        Args:
            title: Section title (e.g., "Results saved to")
            base_path: Base directory path
            files: List of file paths
            is_secondary: Whether this is secondary info (displayed dimmed)
        """
        self._output_sections.append({
            "title": title,
            "base_path": base_path,
            "files": files,
            "is_secondary": is_secondary
        })
    
    def display(self):
        """Display all output sections in a consistent format."""
        if not self._output_sections:
            return
            
        # Get project root for relative path display
        project_root = Path.cwd()
        
        for section in self._output_sections:
            # Format base path
            try:
                display_base = section["base_path"].relative_to(project_root)
                display_base = f"./{display_base}"
            except ValueError:
                display_base = section["base_path"]
            
            # Build display text
            lines = [f"{section['title']}: {display_base}"]
            
            # Add file list
            for file_path in section["files"]:
                try:
                    relative_path = file_path.relative_to(project_root)
                    relative_path = f"./{relative_path}"
                except ValueError:
                    relative_path = file_path
                lines.append(f"  • {relative_path}")
            
            # Display all sections with same formatting
            display_text = "\n".join(lines)
            self.console.print(display_text)
            
            # Add spacing between sections
            if section != self._output_sections[-1]:
                self.console.print()
    
    def display_in_panel(self, panel_title: str = "Analysis Output"):
        """Display all outputs in a styled panel."""
        if not self._output_sections:
            return
            
        # Build content for panel
        content_lines = []
        project_root = Path.cwd()
        
        for i, section in enumerate(self._output_sections):
            # Format base path
            try:
                display_base = section["base_path"].relative_to(project_root)
                display_base = f"./{display_base}"
            except ValueError:
                display_base = section["base_path"]
            
            # Add section title with consistent formatting
            content_lines.append(f"[bold]{section['title']}:[/bold] {display_base}")
            
            # Add files
            for file_path in section["files"]:
                try:
                    relative_path = file_path.relative_to(project_root)
                    relative_path = f"./{relative_path}"
                except ValueError:
                    relative_path = file_path
                    
                content_lines.append(f"  • {relative_path}")
            
            # Add spacing between sections (but not after last)
            if i < len(self._output_sections) - 1:
                content_lines.append("")
        
        # Create and display panel
        panel = Panel(
            "\n".join(content_lines),
            title=panel_title,
            expand=False,
            border_style="blue"
        )
        self.console.print(panel)