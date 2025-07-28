#!/usr/bin/env python3
"""
Simplified demo loader that doesn't require all the dependencies
"""
import json
import sys
import time
import platform
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def generate_critical_findings(results):
    """Generate critical findings based on analysis patterns"""
    findings = []
    
    # Helper to get full descriptions
    hazards = {h['identifier']: h for h in results.get('hazard_identification', {}).get('hazards', [])}
    losses = {l['identifier']: l for l in results.get('loss_identification', {}).get('losses', [])}
    constraints = {c['identifier']: c for c in results.get('security_constraints', {}).get('security_constraints', [])}
    adversaries = {a['adversary_class']: a for a in results.get('stakeholder_analyst', {}).get('adversaries', [])}
    
    # Option A: Direct Mappings
    # Find hazards that map to catastrophic losses
    if 'hazard_identification' in results and 'loss_identification' in results:
        mappings = results['hazard_identification'].get('hazard_loss_mappings', [])
        for mapping in mappings:
            if mapping['relationship_strength'] == 'direct':
                loss = losses.get(mapping['loss_id'])
                hazard = hazards.get(mapping['hazard_id'])
                if loss and hazard and loss.get('severity_classification', {}).get('magnitude') == 'catastrophic':
                    findings.append(
                        f"[Direct Mapping - Catastrophic Loss] {mapping['hazard_id']} maps directly to {mapping['loss_id']}\n"
                        f"  Hazard: {hazard['description']}\n"
                        f"  Loss: {loss['description']}"
                    )
    
    # Find losses with multiple dependencies
    if 'loss_identification' in results:
        deps = results['loss_identification'].get('dependencies', [])
        dep_counts = {}
        for dep in deps:
            primary = dep['primary_loss_id']
            if primary not in dep_counts:
                dep_counts[primary] = []
            dep_counts[primary].append(dep['dependent_loss_id'])
        
        for primary_id, dependent_ids in dep_counts.items():
            if len(dependent_ids) >= 2:
                primary_loss = losses.get(primary_id)
                if primary_loss:
                    findings.append(
                        f"[Multiple Dependencies] {primary_id} triggers {len(dependent_ids)} other losses\n"
                        f"  Primary loss: {primary_loss['description']}\n"
                        f"  Triggers: {', '.join(dependent_ids)}"
                    )
    
    # Find hazards addressed by mandatory constraints
    if 'security_constraints' in results:
        constraint_mappings = results['security_constraints'].get('constraint_hazard_mappings', [])
        mandatory_constraints = [c for c in constraints.values() if c['enforcement_level'] == 'mandatory']
        for constraint in mandatory_constraints[:2]:  # Limit to avoid too many findings
            hazard_ids = [m['hazard_id'] for m in constraint_mappings if m['constraint_id'] == constraint['identifier']]
            if hazard_ids:
                findings.append(
                    f"[Mandatory Constraint] {constraint['identifier']} addresses {len(hazard_ids)} hazard(s)\n"
                    f"  Constraint: {constraint['constraint_statement']}\n"
                    f"  Addresses: {', '.join(hazard_ids)}"
                )
    
    # Option B: Intersection Analysis
    # Hazard + Loss + Adversary intersections
    if all(k in results for k in ['hazard_identification', 'loss_identification', 'stakeholder_analyst']):
        mappings = results['hazard_identification'].get('hazard_loss_mappings', [])
        for mapping in mappings:
            hazard = hazards.get(mapping['hazard_id'])
            loss = losses.get(mapping['loss_id'])
            if hazard and loss and mapping['relationship_strength'] == 'direct':
                # Check adversary interest
                for adv_class, adv in adversaries.items():
                    targets = adv.get('mission_targets', {}).get('interested_in', [])
                    if any(target in hazard['description'].lower() or target in loss['description'].lower() for target in targets):
                        findings.append(
                            f"[Intersection: Hazard-Loss-Adversary] {mapping['hazard_id']} + {mapping['loss_id']} + {adv_class}\n"
                            f"  Hazard: {hazard['description']}\n"
                            f"  Loss: {loss['description']}\n"
                            f"  Adversary: {adv_class.replace('_', ' ').title()} (Sophistication: {adv['profile']['sophistication']})"
                        )
                        break
    
    # Dependency chains
    if 'loss_identification' in results:
        deps = results['loss_identification'].get('dependencies', [])
        for dep1 in deps:
            for dep2 in deps:
                if dep1['dependent_loss_id'] == dep2['primary_loss_id']:
                    for dep3 in deps:
                        if dep2['dependent_loss_id'] == dep3['primary_loss_id']:
                            findings.append(
                                f"[Dependency Chain - 3 Levels] {dep1['primary_loss_id']} → {dep1['dependent_loss_id']} → {dep2['dependent_loss_id']} → {dep3['dependent_loss_id']}\n"
                                f"  Chain type: {dep1['dependency_type']} → {dep2['dependency_type']} → {dep3['dependency_type']}"
                            )
                        else:
                            findings.append(
                                f"[Dependency Chain] {dep1['primary_loss_id']} → {dep1['dependent_loss_id']} → {dep2['dependent_loss_id']}\n"
                                f"  Chain type: {dep1['dependency_type']} → {dep2['dependency_type']}\n"
                                f"  Time relationship: {dep1['time_relationship']['sequence']} → {dep2['time_relationship']['sequence']}"
                            )
                    break
    
    # Multiple hazards mapping to same loss
    if 'hazard_identification' in results:
        loss_hazard_map = {}
        for mapping in results['hazard_identification'].get('hazard_loss_mappings', []):
            loss_id = mapping['loss_id']
            if loss_id not in loss_hazard_map:
                loss_hazard_map[loss_id] = []
            loss_hazard_map[loss_id].append(mapping['hazard_id'])
        
        for loss_id, hazard_ids in loss_hazard_map.items():
            if len(hazard_ids) >= 3:
                loss = losses.get(loss_id)
                if loss:
                    hazard_descs = [hazards.get(hid, {}).get('hazard_category', '') for hid in hazard_ids[:3]]
                    findings.append(
                        f"[Multiple Hazards → Single Loss] {len(hazard_ids)} hazards target {loss_id}\n"
                        f"  Loss: {loss['description']}\n"
                        f"  Hazards: {', '.join(hazard_ids[:3])} (categories: {', '.join(hazard_descs)})"
                    )
    
    # Option C: Critical Pattern Detection
    # Hazards with no preventive constraints
    if 'security_constraints' in results and 'hazard_identification' in results:
        constraint_mappings = results['security_constraints'].get('constraint_hazard_mappings', [])
        
        # Build hazard->constraints map
        hazard_constraints = {}
        for mapping in constraint_mappings:
            hid = mapping['hazard_id']
            if hid not in hazard_constraints:
                hazard_constraints[hid] = []
            constraint = constraints.get(mapping['constraint_id'])
            if constraint:
                hazard_constraints[hid].append(constraint)
        
        # Find hazards with only detective/corrective constraints
        for hazard_id, hazard in hazards.items():
            hazard_cs = hazard_constraints.get(hazard_id, [])
            preventive_count = sum(1 for c in hazard_cs if c['constraint_type'] == 'preventive')
            detective_count = sum(1 for c in hazard_cs if c['constraint_type'] == 'detective')
            corrective_count = sum(1 for c in hazard_cs if c['constraint_type'] == 'corrective')
            
            if hazard_cs and preventive_count == 0 and (detective_count > 0 or corrective_count > 0):
                findings.append(
                    f"[No Preventive Control] {hazard_id} has no preventive constraints\n"
                    f"  Hazard: {hazard['description']}\n"
                    f"  Controls: {detective_count} detective, {corrective_count} corrective"
                )
    
    # Return unique findings, limited to avoid overwhelming the user
    seen = set()
    unique_findings = []
    for f in findings:
        # Use first line as key for uniqueness
        key = f.split('\n')[0]
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)
    
    return unique_findings[:10]  # Show up to 10 critical findings

def generate_markdown_report(results):
    """Generate markdown report from results"""
    
    report = []
    report.append("# STPA-Sec Step 1 Analysis Report - Digital Banking Platform")
    
    # Get timestamp with timezone
    import os
    
    # When running in Docker, we're in UTC unless TZ is set
    # For clarity, always show the timezone explicitly
    utc_time = datetime.utcnow()
    
    # Check if we have a TZ environment variable (for future Docker config)
    tz = os.environ.get('TZ', 'UTC')
    
    if tz == 'UTC' or 'UTC' in str(time.tzname):
        # Running in UTC (Docker default)
        report.append(f"\n**Generated:** {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        # Add local time reference for US East Coast
        from datetime import timedelta
        # EDT is UTC-4 in summer
        edt_time = utc_time - timedelta(hours=4)
        report.append(f"**Local Time (US Eastern):** {edt_time.strftime('%Y-%m-%d %H:%M:%S')} EDT")
    else:
        # Running with configured timezone
        local_time = datetime.now()
        report.append(f"\n**Generated:** {local_time.strftime('%Y-%m-%d %H:%M:%S')} {tz}")
    report.append("\n---\n")
    
    # Mission Statement
    if 'mission_analyst' in results:
        mission = results['mission_analyst']
        ps = mission['problem_statement']
        report.append("## Mission Statement")
        report.append(f"\n**Purpose:** {ps['purpose_what']}")
        report.append(f"\n**Method:** {ps['method_how']}")
        report.append(f"\n**Goals:** {ps['goals_why']}\n")
    
    # Losses
    if 'loss_identification' in results:
        losses = results['loss_identification']
        report.append("## Losses")
        report.append(f"\n**Total:** {losses.get('loss_count', len(losses.get('losses', [])))}")
        
        # Show loss categories breakdown
        if 'loss_categories' in losses:
            categories = losses['loss_categories']
            report.append("\n### Losses by Category")
            for category, count in categories.items():
                report.append(f"- {category.capitalize()}: {count}")
            report.append("")
        
        report.append("\n| ID | Description | Category | Severity |")
        report.append("|---|---|---|---|")
        for loss in losses.get('losses', []):
            report.append(f"| {loss['identifier']} | {loss['description']} | {loss['loss_category']} | {loss['severity_classification']['magnitude']} |")
        report.append("")
        
        # Add loss dependencies immediately after losses
        if 'dependencies' in losses:
            report.append("### Loss Dependencies")
            report.append(f"\n**Total:** {len(losses.get('dependencies', []))}")
            report.append("\n| Primary Loss | Dependent Loss | Type | Strength | Timing | Rationale |")
            report.append("|---|---|---|---|---|---|")
            for dep in losses.get('dependencies', []):
                rationale = dep.get('rationale', '').replace('|', '\\|')
                timing = dep.get('time_relationship', {}).get('sequence', '')
                report.append(f"| {dep['primary_loss_id']} | {dep['dependent_loss_id']} | {dep['dependency_type']} | {dep['dependency_strength']} | {timing} | {rationale} |")
            report.append("")
    
    # Hazards
    if 'hazard_identification' in results:
        hazards = results['hazard_identification']
        report.append("## Hazards")
        report.append(f"\n**Total:** {hazards.get('hazard_count', len(hazards.get('hazards', [])))}")
        
        # Show hazard categories breakdown
        if 'hazard_categories' in hazards:
            categories = hazards['hazard_categories']
            report.append("\n### Hazards by Category")
            for category, count in categories.items():
                report.append(f"- {category.replace('_', ' ').title()}: {count}")
            report.append("")
        
        report.append("\n| ID | Description | Category |")
        report.append("|---|---|---|")
        for hazard in hazards.get('hazards', []):
            report.append(f"| {hazard['identifier']} | {hazard['description']} | {hazard['hazard_category']} |")
        report.append("")
        
        # Add hazard-loss mappings
        if 'hazard_loss_mappings' in hazards:
            report.append("### Hazard-Loss Mappings")
            report.append(f"\n**Total:** {len(hazards.get('hazard_loss_mappings', []))}")
            report.append("\n| Hazard | Loss | Relationship | Rationale |")
            report.append("|---|---|---|---|")
            for mapping in hazards.get('hazard_loss_mappings', []):
                rationale = mapping.get('rationale', '').replace('|', '\\|')
                report.append(f"| {mapping['hazard_id']} | {mapping['loss_id']} | {mapping['relationship_strength']} | {rationale} |")
            report.append("")
    
    # Security Constraints
    if 'security_constraints' in results:
        constraints = results['security_constraints']
        report.append("## Security Constraints")
        report.append(f"\n**Total:** {constraints.get('constraint_count', len(constraints.get('security_constraints', [])))}")
        
        # Type breakdown
        if 'constraint_types' in constraints:
            types = constraints['constraint_types']
            report.append("\n### Security Constraints by Type")
            report.append(f"- Preventive: {types.get('preventive', 0)}")
            report.append(f"- Detective: {types.get('detective', 0)}")
            report.append(f"- Corrective: {types.get('corrective', 0)}")
            report.append(f"- Compensating: {types.get('compensating', 0)}")
            report.append("")
        
        report.append("\n| ID | Constraint Statement | Type | Level |")
        report.append("|---|---|---|---|")
        for constraint in constraints.get('security_constraints', []):
            report.append(f"| {constraint['identifier']} | {constraint['constraint_statement']} | {constraint['constraint_type']} | {constraint['enforcement_level']} |")
        report.append("")
        
        # Add constraint-hazard mappings
        if 'constraint_hazard_mappings' in constraints:
            report.append("### Constraint-Hazard Mappings")
            report.append(f"\n**Total:** {len(constraints.get('constraint_hazard_mappings', []))}")
            report.append("\n| Constraint | Hazard | Relationship |")
            report.append("|---|---|---|")
            for mapping in constraints.get('constraint_hazard_mappings', []):
                report.append(f"| {mapping['constraint_id']} | {mapping['hazard_id']} | {mapping['relationship_type']} |")
            report.append("")
    
    # System Boundaries
    if 'system_boundaries' in results:
        boundaries = results['system_boundaries']
        report.append("## System Boundaries")
        report.append(f"\n**Total:** {len(boundaries.get('system_boundaries', []))}")
        
        report.append("\n### All System Boundaries")
        report.append("\n| Name | Type | Description | Elements |")
        report.append("|---|---|---|---|")
        for boundary in boundaries.get('system_boundaries', []):
            name = boundary['boundary_name']
            btype = boundary['boundary_type']
            desc = boundary['description'].replace('|', '\\|')
            if 'elements' in boundary:
                inside = len([e for e in boundary['elements'] if e['position'] == 'inside'])
                outside = len([e for e in boundary['elements'] if e['position'] == 'outside'])
                interface = len([e for e in boundary['elements'] if e['position'] == 'interface'])
                elements = f"{inside} inside, {outside} outside, {interface} at interface"
            else:
                elements = "No elements defined"
            report.append(f"| {name} | {btype} | {desc} | {elements} |")
        report.append("")
    
    # Stakeholders
    if 'stakeholder_analyst' in results:
        stakeholders = results['stakeholder_analyst']
        report.append("## Stakeholders")
        report.append(f"\n**Total:** {len(stakeholders.get('stakeholders', []))}")
        report.append("\n| Name | Type | Criticality | Primary Needs |")
        report.append("|---|---|---|---|")
        for sh in stakeholders.get('stakeholders', []):
            needs = ", ".join(sh.get('mission_perspective', {}).get('primary_needs', []))
            report.append(f"| {sh['name']} | {sh['stakeholder_type']} | {sh.get('criticality', 'N/A')} | {needs} |")
        
        # Adversaries
        report.append("\n## Adversaries")
        report.append(f"\n**Total:** {len(stakeholders.get('adversaries', []))}")
        report.append("\n| Class | Sophistication | Resources | Primary Interest |")
        report.append("|---|---|---|---|")
        for adv in stakeholders.get('adversaries', []):
            profile = adv['profile']
            report.append(f"| {adv['adversary_class']} | {profile['sophistication']} | {profile['resources']} | {profile['primary_interest']} |")
        report.append("")
    
    # Calculate metrics dynamically
    report.append("## Analysis Metrics")
    
    # Calculate total findings
    total_findings = 0
    if 'loss_identification' in results:
        total_findings += results['loss_identification'].get('loss_count', 0)
        total_findings += len(results['loss_identification'].get('dependencies', []))
    if 'hazard_identification' in results:
        total_findings += results['hazard_identification'].get('hazard_count', 0)
        total_findings += len(results['hazard_identification'].get('hazard_loss_mappings', []))
    if 'security_constraints' in results:
        total_findings += results['security_constraints'].get('constraint_count', 0)
        total_findings += len(results['security_constraints'].get('constraint_hazard_mappings', []))
    if 'system_boundaries' in results:
        total_findings += len(results['system_boundaries'].get('system_boundaries', []))
    if 'stakeholder_analyst' in results:
        total_findings += len(results['stakeholder_analyst'].get('stakeholders', []))
        total_findings += len(results['stakeholder_analyst'].get('adversaries', []))
    
    report.append(f"\n- Total findings: {total_findings}")
    report.append(f"- Loss dependencies: {len(results.get('loss_identification', {}).get('dependencies', []))}")
    report.append(f"- Hazard-loss mappings: {len(results.get('hazard_identification', {}).get('hazard_loss_mappings', []))}")
    report.append(f"- Security constraints: {results.get('security_constraints', {}).get('constraint_count', 0)}")
    report.append(f"- Constraint-hazard mappings: {len(results.get('security_constraints', {}).get('constraint_hazard_mappings', []))}")
    report.append(f"- System boundaries: {len(results.get('system_boundaries', {}).get('system_boundaries', []))}")
    
    # Generate critical findings programmatically
    critical_findings = generate_critical_findings(results)
    if critical_findings:
        report.append("\n## Critical Findings")
        for i, finding in enumerate(critical_findings, 1):
            # Format multi-line findings for markdown
            lines = finding.split('\n')
            report.append(f"\n### Finding {i}: {lines[0]}")
            for line in lines[1:]:
                if line.strip():
                    report.append(line)
    
    report.append("\n---")
    report.append("\n*This analysis was generated using STPA-Sec Step 1 methodology*")
    
    return "\n".join(report)

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
                     "security_constraints.json", "system_boundaries.json",
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
    
    # Losses
    if 'loss_identification' in results:
        losses = results['loss_identification']
        console.print("\n[bold]Losses:[/bold]")
        console.print(f"Total: {losses.get('loss_count', 0)} losses")
        
        # Show loss categories breakdown
        if 'loss_categories' in losses:
            categories = losses['loss_categories']
            console.print("\n[bold]Losses by Category:[/bold]")
            for category, count in categories.items():
                console.print(f"  • {category.capitalize()}: {count}")
        
        console.print("\nAll Losses:")
        for loss in losses.get('losses', []):
            console.print(f"  • {loss['identifier']}: {loss['description']}")
            console.print(f"    Category: {loss['loss_category']}, Severity: {loss['severity_classification']['magnitude']}")
        
        # Show loss dependencies immediately after losses
        if 'dependencies' in losses:
            console.print("\n[bold]Loss Dependencies:[/bold]")
            for dep in losses.get('dependencies', []):
                console.print(f"  • {dep['primary_loss_id']} → {dep['dependent_loss_id']} ({dep['dependency_type']})")
                console.print(f"    Strength: {dep['dependency_strength']}, Timing: {dep['time_relationship']['sequence']}")
                if 'rationale' in dep:
                    console.print(f"    Rationale: {dep['rationale']}")
    
    # Hazards
    if 'hazard_identification' in results:
        hazards = results['hazard_identification']
        console.print("\n[bold]Hazards:[/bold]")
        console.print(f"Total: {hazards.get('hazard_count', 0)} hazards")
        
        # Show hazard categories breakdown
        if 'hazard_categories' in hazards:
            categories = hazards['hazard_categories']
            console.print("\n[bold]Hazards by Category:[/bold]")
            for category, count in categories.items():
                console.print(f"  • {category.replace('_', ' ').title()}: {count}")
        
        console.print("\nAll Hazards:")
        for hazard in hazards.get('hazards', []):
            console.print(f"  • {hazard['identifier']}: {hazard['description']}")
            console.print(f"    Category: {hazard['hazard_category']}")
        
        # Show hazard-loss mappings
        if 'hazard_loss_mappings' in hazards:
            console.print("\n[bold]Hazard-Loss Mappings:[/bold]")
            for mapping in hazards.get('hazard_loss_mappings', []):
                console.print(f"  • {mapping['hazard_id']} → {mapping['loss_id']} ({mapping['relationship_strength']})")
                if 'rationale' in mapping:
                    console.print(f"    Rationale: {mapping['rationale']}")
    
    # Security Constraints (moved after hazards)
    if 'security_constraints' in results:
        constraints = results['security_constraints']
        console.print("\n[bold]Security Constraints:[/bold]")
        console.print(f"Total: {constraints.get('constraint_count', 0)} constraints")
        
        # Show constraint types
        console.print("\n[bold]Security Constraints by Type:[/bold]")
        if 'constraint_types' in constraints:
            types = constraints['constraint_types']
            console.print(f"  • Preventive: {types.get('preventive', 0)}")
            console.print(f"  • Detective: {types.get('detective', 0)}")
            console.print(f"  • Corrective: {types.get('corrective', 0)}")
            console.print(f"  • Compensating: {types.get('compensating', 0)}")
        
        # Show all constraints
        console.print("\nAll Security Constraints:")
        for constraint in constraints.get('security_constraints', []):
            console.print(f"  • {constraint['identifier']}: {constraint['constraint_statement']}")
            console.print(f"    Type: {constraint['constraint_type']}, Level: {constraint['enforcement_level']}")
        
        # Show constraint-hazard mappings
        if 'constraint_hazard_mappings' in constraints:
            console.print("\n[bold]Constraint-Hazard Mappings:[/bold]")
            for mapping in constraints.get('constraint_hazard_mappings', []):
                console.print(f"  • {mapping['constraint_id']} → {mapping['hazard_id']} ({mapping['relationship_type']})")
    
    # System Boundaries (moved after constraints)
    if 'system_boundaries' in results:
        boundaries = results['system_boundaries']
        console.print("\n[bold]System Boundaries:[/bold]")
        console.print(f"Total: {len(boundaries.get('system_boundaries', []))} boundaries")
        
        console.print("\nAll System Boundaries:")
        for boundary in boundaries.get('system_boundaries', []):
            console.print(f"  • {boundary['boundary_name']} ({boundary['boundary_type']})")
            console.print(f"    {boundary['description']}")
            if 'elements' in boundary:
                inside = [e for e in boundary['elements'] if e['position'] == 'inside']
                outside = [e for e in boundary['elements'] if e['position'] == 'outside']
                interface = [e for e in boundary['elements'] if e['position'] == 'interface']
                console.print(f"    Elements: {len(inside)} inside, {len(outside)} outside, {len(interface)} at interface")
    
    # Enhanced Stakeholders display
    if 'stakeholder_analyst' in results:
        stakeholders = results['stakeholder_analyst']
        console.print("\n[bold]Stakeholders:[/bold]")
        for sh in stakeholders.get('stakeholders', []):
            console.print(f"  • {sh['name']} ({sh['stakeholder_type']})")
            console.print(f"    Criticality: {sh.get('criticality', 'N/A')}")
            needs = sh.get('mission_perspective', {}).get('primary_needs', [])
            if needs:
                console.print(f"    Primary needs: {', '.join(needs)}")
        
        # Enhanced Adversaries display
        console.print("\n[bold]Adversaries:[/bold]")
        for adv in stakeholders.get('adversaries', []):
            profile = adv['profile']
            console.print(f"  • {adv['adversary_class'].replace('_', ' ').title()}")
            console.print(f"    Sophistication: {profile['sophistication']}, Resources: {profile['resources']}")
            console.print(f"    Primary interest: {profile['primary_interest']}")
            targets = adv.get('mission_targets', {}).get('interested_in', [])
            if targets:
                console.print(f"    Targets: {', '.join(targets)}")
    
    # Create summary table
    table = Table(title="Analysis Summary", show_header=True)
    table.add_column("Component", style="cyan", width=25)
    table.add_column("Count", justify="right", style="green")
    
    # Add counts to table
    if 'loss_identification' in results:
        loss_count = results['loss_identification'].get('loss_count', 0)
        table.add_row("Losses Identified", str(loss_count))
    
    if 'hazard_identification' in results:
        hazard_count = results['hazard_identification'].get('hazard_count', 0)
        table.add_row("Hazards Identified", str(hazard_count))
    
    if 'security_constraints' in results:
        constraint_count = results['security_constraints'].get('constraint_count', 0)
        table.add_row("Security Constraints", str(constraint_count))
    
    if 'system_boundaries' in results:
        boundary_count = len(results['system_boundaries'].get('system_boundaries', []))
        table.add_row("System Boundaries", str(boundary_count))
    
    if 'stakeholder_analyst' in results:
        stakeholder_count = len(results['stakeholder_analyst'].get('stakeholders', []))
        adversary_count = len(results['stakeholder_analyst'].get('adversaries', []))
        table.add_row("Stakeholders Identified", str(stakeholder_count))
        table.add_row("Adversaries Profiled", str(adversary_count))
    
    console.print("\n")
    console.print(table)
    
    # Calculate metrics dynamically
    console.print("\n[bold]Analysis Metrics:[/bold]")
    
    # Calculate total findings
    total_findings = 0
    if 'loss_identification' in results:
        total_findings += results['loss_identification'].get('loss_count', 0)
        total_findings += len(results['loss_identification'].get('dependencies', []))
    if 'hazard_identification' in results:
        total_findings += results['hazard_identification'].get('hazard_count', 0)
        total_findings += len(results['hazard_identification'].get('hazard_loss_mappings', []))
    if 'security_constraints' in results:
        total_findings += results['security_constraints'].get('constraint_count', 0)
        total_findings += len(results['security_constraints'].get('constraint_hazard_mappings', []))
    if 'system_boundaries' in results:
        total_findings += len(results['system_boundaries'].get('system_boundaries', []))
    if 'stakeholder_analyst' in results:
        total_findings += len(results['stakeholder_analyst'].get('stakeholders', []))
        total_findings += len(results['stakeholder_analyst'].get('adversaries', []))
    
    console.print(f"  • Total findings: {total_findings}")
    console.print(f"  • Loss dependencies: {len(results.get('loss_identification', {}).get('dependencies', []))}")
    console.print(f"  • Hazard-loss mappings: {len(results.get('hazard_identification', {}).get('hazard_loss_mappings', []))}")
    console.print(f"  • Security constraints: {results.get('security_constraints', {}).get('constraint_count', 0)}")
    console.print(f"  • Constraint-hazard mappings: {len(results.get('security_constraints', {}).get('constraint_hazard_mappings', []))}")
    console.print(f"  • System boundaries: {len(results.get('system_boundaries', {}).get('system_boundaries', []))}")
        
    # Generate critical findings programmatically
    critical_findings = generate_critical_findings(results)
    if critical_findings:
        console.print("\n[bold]Critical Findings:[/bold]")
        for i, finding in enumerate(critical_findings, 1):
            console.print(f"\n{i}. {finding}")
    
    console.print("\n[bold]Analysis Output:[/bold]")
    console.print("Full results available in: ./demo/banking-analysis/results/")
    console.print("  • mission_analyst.json")
    console.print("  • loss_identification.json")
    console.print("  • hazard_identification.json")
    console.print("  • stakeholder_analyst.json")
    console.print("  • security_constraints.json")
    console.print("  • system_boundaries.json")
    console.print("  • validation.json")
    
    # Generate and save markdown report
    markdown_report = generate_markdown_report(results)
    report_path = demo_path / "step1_analysis_report.md"
    with open(report_path, 'w') as f:
        f.write(markdown_report)
    
    console.print(f"\n[green]Markdown report saved to:[/green] {report_path}")
    
    console.print("\n[dim]This is a pre-packaged demo analysis. To run your own analysis:[/dim]")
    console.print("[dim]./ai-sec analyze --config configs/standard-analysis.yaml[/dim]\n")

if __name__ == "__main__":
    load_demo()