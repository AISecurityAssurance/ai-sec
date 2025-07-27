#!/usr/bin/env python3
"""
Simplified demo loader that doesn't require all the dependencies
"""
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_demo():
    """Load and display the pre-packaged demo analysis"""
    
    demo_path = Path("demo/banking-analysis")
    
    if not demo_path.exists():
        console.print(f"[red]Demo not found at {demo_path}[/red]")
        sys.exit(1)
    
    # Load results
    results_dir = demo_path / "results"
    
    results = {}
    for json_file in ["mission_analyst.json", "loss_identification.json", 
                     "hazard_identification.json", "stakeholder_analyst.json", 
                     "validation.json"]:
        file_path = results_dir / json_file
        if file_path.exists():
            with open(file_path, 'r') as f:
                results[json_file.replace('.json', '')] = json.load(f)
    
    # Display summary
    console.print("\n[bold green]Step 1 STPA-Sec Analysis - Banking Demo[/bold green]\n")
    
    # Mission summary
    if 'mission_analyst' in results:
        mission = results['mission_analyst']
        ps = mission['problem_statement']
        console.print(Panel(
            f"[bold]Purpose:[/bold] {ps['purpose_what']}\n\n"
            f"[bold]Method:[/bold] {ps['method_how']}\n\n"
            f"[bold]Goals:[/bold] {ps['goals_why']}",
            title="Mission Statement",
            border_style="blue"
        ))
    
    # Create summary table
    table = Table(title="Analysis Summary", show_header=True)
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Count", justify="right", style="green")
    table.add_column("Key Findings", style="yellow", width=50)
    
    # Losses
    if 'loss_identification' in results:
        losses = results['loss_identification']
        loss_count = losses.get('loss_count', len(losses.get('losses', [])))
        key_losses = [l['identifier'] + ": " + l['description'][:40] + "..." 
                     for l in losses.get('losses', [])[:2]]
        table.add_row("Losses", str(loss_count), "\n".join(key_losses))
    
    # Hazards
    if 'hazard_identification' in results:
        hazards = results['hazard_identification']
        hazard_count = hazards.get('hazard_count', len(hazards.get('hazards', [])))
        key_hazards = [h['identifier'] + ": " + h['description'][:40] + "..." 
                      for h in hazards.get('hazards', [])[:2]]
        table.add_row("Hazards", str(hazard_count), "\n".join(key_hazards))
    
    # Stakeholders
    if 'stakeholder_analyst' in results:
        stakeholders = results['stakeholder_analyst']
        stakeholder_count = len(stakeholders.get('stakeholders', []))
        adversary_count = len(stakeholders.get('adversaries', []))
        key_info = [
            f"{stakeholder_count} stakeholders identified",
            f"{adversary_count} adversary types analyzed"
        ]
        table.add_row("Stakeholders", str(stakeholder_count + adversary_count), 
                     "\n".join(key_info))
    
    console.print("\n")
    console.print(table)
    
    # Validation summary
    if 'validation' in results:
        validation = results['validation']
        quality = validation.get('quality_metrics', {})
        console.print(f"\n[bold]Quality Score:[/bold] {quality.get('overall_score', 0) * 100:.0f}%")
        console.print(f"[bold]Status:[/bold] {validation.get('overall_status', 'Unknown')}")
        
        if 'executive_summary' in validation:
            console.print("\n[bold]Executive Summary:[/bold]")
            console.print(Panel(validation['executive_summary'], border_style="green"))
    
    console.print("\n[dim]This is a pre-packaged demo analysis. To run your own analysis, use:[/dim]")
    console.print("[dim]./ai-sec analyze --config configs/standard-analysis.yaml[/dim]\n")

if __name__ == "__main__":
    load_demo()