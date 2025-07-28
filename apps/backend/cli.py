#!/usr/bin/env python3
"""
STPA-Sec Step 1 Analysis CLI

Usage:
    python cli.py analyze --config analysis-config.yaml
    python cli.py export --analysis-id <id> --format json
"""
import argparse
import asyncio
import os
import sys
import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import asyncpg
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agents.step1_agents import Step1Coordinator
from core.database import create_database_pool, run_migrations
from config.settings import settings, ModelProvider, ModelConfig

console = Console()


class Step1CLI:
    """Command-line interface for STPA-Sec Step 1 analysis"""
    
    def __init__(self):
        self.console = console
        
    async def analyze(self, config_path: str):
        """Run Step 1 analysis based on configuration file"""
        
        # Load configuration
        config = self._load_config(config_path)
        
        # Validate configuration
        self._validate_config(config)
        
        # Set up environment variables for API keys
        self._setup_api_keys(config)
        
        # Create analysis database
        db_name, timestamp = await self._create_analysis_database(config)
        
        # Store timestamp for consistent file naming
        self._timestamp = timestamp
        
        # Read system description
        system_description = self._read_system_description(config)
        
        # Run analysis with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Running Step 1 Analysis...", total=None)
            
            try:
                # Connect to database
                db_host = os.getenv('DB_HOST', 'postgres')
                db_url = f"postgresql://sa_user:sa_password@{db_host}:5432/{db_name}"
                db_conn = await asyncpg.connect(db_url)
                
                # Create coordinator with execution mode
                execution_mode = config.get('execution', {}).get('mode', 'standard')
                coordinator = Step1Coordinator(
                    db_connection=db_conn,
                    execution_mode=execution_mode,
                    db_name=db_name
                )
                
                # Run analysis
                results = await coordinator.perform_analysis(
                    system_description=system_description,
                    analysis_name=config['analysis']['name']
                )
                
                # Save results
                await self._save_results(config, results, db_name)
                
                # Display summary
                self._display_results_summary(results, execution_mode)
                
                # Display completeness check
                if 'completeness_check' in results:
                    self._display_completeness_check(results['completeness_check'])
                
                # Display file output locations
                self._display_output_files()
                
            finally:
                await db_conn.close()
        
        self.console.print(f"\n✅ Analysis complete! Database: {db_name}")
        return db_name
    
    async def demo(self, demo_name: str = "banking-analysis"):
        """Load and display pre-packaged demo analysis"""
        
        # Find demo directory
        demo_path = Path(__file__).parent / "demo" / demo_name
        
        if not demo_path.exists():
            self.console.print(f"[red]Demo '{demo_name}' not found at {demo_path}[/red]")
            sys.exit(1)
        
        # Create demo config
        demo_config = {
            'analysis': {
                'name': f'Demo: {demo_name}',
                'output_dir': '/analyses'  # Use mounted analyses directory
            },
            'model': {
                'provider': 'demo',
                'name': 'pre-packaged'
            },
            'input': {
                'type': 'demo',
                'path': str(demo_path)
            },
            'execution': {
                'mode': 'enhanced'
            }
        }
        
        # Create analysis database
        db_name, timestamp = await self._create_analysis_database(demo_config)
        
        # Store timestamp for consistent file naming
        self._timestamp = timestamp
        
        # Display loading message
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Loading demo analysis '{demo_name}'...", total=None)
            
            try:
                # Connect to database
                db_host = os.getenv('DB_HOST', 'postgres')
                db_url = f"postgresql://sa_user:sa_password@{db_host}:5432/{db_name}"
                db_conn = await asyncpg.connect(db_url)
                
                # Create coordinator
                coordinator = Step1Coordinator(
                    db_connection=db_conn,
                    execution_mode="enhanced",  # Demo uses enhanced mode
                    db_name=db_name
                )
                
                # Load existing analysis
                results = await coordinator.load_existing_analysis(str(demo_path))
                
                # Save results just like regular analysis
                await self._save_results(demo_config, results, db_name)
                
                # Display summary
                self._display_results_summary(results, "enhanced")
                
                # Display completeness check
                if 'completeness_check' in results:
                    self._display_completeness_check(results['completeness_check'])
                
                # Display file output locations
                self._display_output_files()
                
            finally:
                await db_conn.close()
        
        self.console.print(f"\n✅ Analysis complete! Database: {db_name}")
        return db_name
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading config: {e}[/red]")
            sys.exit(1)
    
    def _validate_config(self, config: dict):
        """Validate configuration structure"""
        required = ['analysis', 'model', 'input']
        for key in required:
            if key not in config:
                self.console.print(f"[red]Missing required config section: {key}[/red]")
                sys.exit(1)
    
    def _setup_api_keys(self, config: dict):
        """Set up API keys from environment variables"""
        model_config = config.get('model', {})
        api_key_env = model_config.get('api_key_env')
        
        if api_key_env:
            if api_key_env not in os.environ:
                self.console.print(f"[red]Environment variable {api_key_env} not set[/red]")
                self.console.print(f"Please set it with: export {api_key_env}='your-api-key'")
                sys.exit(1)
            
            # Configure the model provider in settings
            provider = model_config.get('provider', 'ollama')
            if provider == 'openai':
                settings.model_providers['openai'] = ModelConfig(
                    provider=ModelProvider.OPENAI,
                    auth_method='api-key',
                    api_key=os.environ[api_key_env],
                    model=model_config.get('name', 'gpt-4-turbo-preview'),
                    is_enabled=True
                )
                settings.active_provider = ModelProvider.OPENAI
            elif provider == 'ollama':
                settings.model_providers['ollama'] = ModelConfig(
                    provider=ModelProvider.OLLAMA,
                    auth_method='none',
                    api_endpoint=model_config.get('api_endpoint', 'http://localhost:11434'),
                    model=model_config.get('name', 'llama2'),
                    is_enabled=True
                )
                settings.active_provider = ModelProvider.OLLAMA
        
        # Reinitialize llm_manager after setting up API keys
        from core.utils.llm_client import llm_manager
        llm_manager.reinitialize()
    
    async def _create_analysis_database(self, config: dict) -> tuple[str, str]:
        """Create new PostgreSQL database for analysis
        
        Returns:
            Tuple of (db_name, timestamp)
        """
        # Generate timestamp and database name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_name = f"stpa_analysis_{timestamp}"
        
        # Create database
        # Use environment variable or default to Docker service name
        db_host = os.getenv('DB_HOST', 'postgres')
        sys_conn = await asyncpg.connect(
            f"postgresql://sa_user:sa_password@{db_host}:5432/postgres"
        )
        
        try:
            await sys_conn.execute(f'CREATE DATABASE "{db_name}"')
            self.console.print(f"Created database: {db_name}")
            
            # Run migrations
            await sys_conn.close()
            db_conn = await asyncpg.connect(
                f"postgresql://sa_user:sa_password@{db_host}:5432/{db_name}"
            )
            
            # Run migrations (simplified for demo)
            migrations_dir = Path(__file__).parent / "migrations"
            for migration in sorted(migrations_dir.glob("*.sql")):
                self.console.print(f"Running migration: {migration.name}")
                with open(migration) as f:
                    await db_conn.execute(f.read())
            
            await db_conn.close()
            
        finally:
            await sys_conn.close()
        
        return db_name, timestamp
    
    def _read_system_description(self, config: dict) -> str:
        """Read system description from configured source"""
        input_config = config.get('input', {})
        input_type = input_config.get('type', 'file')
        
        if input_type == 'file':
            file_path = input_config.get('path')
            if not file_path:
                self.console.print("[red]No input file specified[/red]")
                sys.exit(1)
            
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            except Exception as e:
                self.console.print(f"[red]Error reading input file: {e}[/red]")
                sys.exit(1)
        
        # Add support for other input types later
        return ""
    
    async def _save_results(self, config: dict, results: dict, db_name: str):
        """Save results in configured formats"""
        # Get project root (two levels up from backend)
        project_root = Path(__file__).parent.parent.parent
        
        # Get timestamp from database name or use stored timestamp
        if hasattr(self, '_timestamp'):
            timestamp = self._timestamp
        else:
            # Extract timestamp from db_name if not available
            timestamp = db_name.replace('stpa_analysis_', '')
        
        # Use configured output_dir or default to root-level analysis directory
        if 'output_dir' in config['analysis']:
            base_dir = Path(config['analysis']['output_dir'])
            # If it's a relative path, make it relative to project root
            if not base_dir.is_absolute():
                base_dir = project_root / base_dir
        else:
            # Default to analysis directory at root level
            base_dir = project_root / 'analysis'
        
        # Create timestamped subdirectory
        output_dir = base_dir / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration (without secrets)
        config_copy = config.copy()
        if 'model' in config_copy and 'api_key' in config_copy['model']:
            del config_copy['model']['api_key']
        
        config_file = output_dir / 'analysis-config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(config_copy, f)
        
        # Save results as JSON
        results_file = output_dir / 'analysis-results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Store output info for display
        self._output_dir = output_dir
        self._saved_files = [config_file, results_file]
        
        # Generate markdown report
        report_file = await self._generate_markdown_report(config, results, output_dir)
        if report_file:
            self._saved_files.append(report_file)
        
        # Export database to the same directory
        await self._export_database(db_name, output_dir)
    
    def _display_results_summary(self, results: dict, execution_mode: str):
        """Display detailed analysis results like the demo"""
        
        self.console.print(f"\n[bold green]Step 1 STPA-Sec Analysis Results ({execution_mode} mode)[/bold green]\n")
        
        # Extract results sections
        analysis_results = results.get('results', {})
        mission_results = analysis_results.get('mission_analyst', {})
        loss_results = analysis_results.get('loss_identification', {})
        hazard_results = analysis_results.get('hazard_identification', {})
        constraint_results = analysis_results.get('security_constraints', {})
        boundary_results = analysis_results.get('system_boundaries', {})
        # Try both possible keys for stakeholder results
        stakeholder_results = analysis_results.get('stakeholder_analyst', {})
        if not stakeholder_results:
            stakeholder_results = analysis_results.get('stakeholder_analysis', {})
        
        # Mission Statement
        if mission_results:
            ps = mission_results.get('problem_statement', {})
            if ps:
                self.console.print(Panel(
                    f"[bold]Purpose:[/bold] {ps.get('purpose_what', 'N/A')}\n\n"
                    f"[bold]Method:[/bold] {ps.get('method_how', 'N/A')}\n\n"
                    f"[bold]Goals:[/bold] {ps.get('goals_why', 'N/A')}",
                    title="Mission Statement",
                    border_style="blue"
                ))
        
        # Losses
        if loss_results:
            self.console.print("\n[bold]Losses:[/bold]")
            self.console.print(f"Total: {loss_results.get('loss_count', 0)} losses")
            
            # Show loss categories breakdown
            if 'loss_categories' in loss_results:
                categories = loss_results['loss_categories']
                self.console.print("\n[bold]Losses by Category:[/bold]")
                for category, count in categories.items():
                    self.console.print(f"  • {category.capitalize()}: {count}")
            
            self.console.print("\nAll Losses:")
            for loss in loss_results.get('losses', []):
                self.console.print(f"  • {loss['identifier']}: {loss['description']}")
                self.console.print(f"    Category: {loss['loss_category']}, Severity: {loss['severity_classification']['magnitude']}")
            
            # Show loss dependencies
            if 'dependencies' in loss_results:
                self.console.print("\n[bold]Loss Dependencies:[/bold]")
                for dep in loss_results.get('dependencies', []):
                    self.console.print(f"  • {dep['primary_loss_id']} → {dep['dependent_loss_id']} ({dep['dependency_type']})")
                    self.console.print(f"    Strength: {dep['dependency_strength']}, Timing: {dep['time_relationship']['sequence']}")
                    if 'rationale' in dep:
                        self.console.print(f"    Rationale: {dep['rationale']}")
        
        # Hazards
        if hazard_results:
            self.console.print("\n[bold]Hazards:[/bold]")
            self.console.print(f"Total: {hazard_results.get('hazard_count', 0)} hazards")
            
            # Show hazard categories breakdown
            if 'hazard_categories' in hazard_results:
                categories = hazard_results['hazard_categories']
                self.console.print("\n[bold]Hazards by Category:[/bold]")
                for category, count in categories.items():
                    self.console.print(f"  • {category.replace('_', ' ').title()}: {count}")
            
            self.console.print("\nAll Hazards:")
            for hazard in hazard_results.get('hazards', []):
                self.console.print(f"  • {hazard['identifier']}: {hazard['description']}")
                self.console.print(f"    Category: {hazard['hazard_category']}")
            
            # Show hazard-loss mappings
            if 'hazard_loss_mappings' in hazard_results:
                self.console.print("\n[bold]Hazard-Loss Mappings:[/bold]")
                for mapping in hazard_results.get('hazard_loss_mappings', []):
                    self.console.print(f"  • {mapping['hazard_id']} → {mapping['loss_id']} ({mapping['relationship_strength']})")
                    if 'rationale' in mapping:
                        self.console.print(f"    Rationale: {mapping['rationale']}")
        
        # Security Constraints
        if constraint_results:
            self.console.print("\n[bold]Security Constraints:[/bold]")
            self.console.print(f"Total: {constraint_results.get('constraint_count', 0)} constraints")
            
            # Show constraint types
            self.console.print("\n[bold]Security Constraints by Type:[/bold]")
            if 'constraint_types' in constraint_results:
                types = constraint_results['constraint_types']
                self.console.print(f"  • Preventive: {types.get('preventive', 0)}")
                self.console.print(f"  • Detective: {types.get('detective', 0)}")
                self.console.print(f"  • Corrective: {types.get('corrective', 0)}")
                self.console.print(f"  • Compensating: {types.get('compensating', 0)}")
            
            # Show all constraints
            self.console.print("\nAll Security Constraints:")
            for constraint in constraint_results.get('security_constraints', []):
                self.console.print(f"  • {constraint['identifier']}: {constraint['constraint_statement']}")
                self.console.print(f"    Type: {constraint['constraint_type']}, Level: {constraint['enforcement_level']}")
            
            # Show constraint-hazard mappings
            self.console.print("\n[bold]Constraint-Hazard Mappings:[/bold]")
            mappings = constraint_results.get('constraint_hazard_mappings', [])
            if mappings:
                for mapping in mappings:
                    self.console.print(f"  • {mapping['constraint_id']} → {mapping['hazard_id']} ({mapping['relationship_type']})")
            else:
                self.console.print("  No findings")
        
        # System Boundaries
        if boundary_results:
            self.console.print("\n[bold]System Boundaries:[/bold]")
            self.console.print(f"Total: {len(boundary_results.get('system_boundaries', []))} boundaries")
            
            self.console.print("\nAll System Boundaries:")
            for boundary in boundary_results.get('system_boundaries', []):
                self.console.print(f"  • {boundary['boundary_name']} ({boundary['boundary_type']})")
                self.console.print(f"    {boundary['description']}")
                if 'elements' in boundary:
                    inside = [e for e in boundary['elements'] if e['position'] == 'inside']
                    outside = [e for e in boundary['elements'] if e['position'] == 'outside']
                    interface = [e for e in boundary['elements'] if e['position'] == 'interface']
                    self.console.print(f"    Elements: {len(inside)} inside, {len(outside)} outside, {len(interface)} at interface")
        
        # Stakeholders
        if stakeholder_results:
            self.console.print("\n[bold]Stakeholders:[/bold]")
            for sh in stakeholder_results.get('stakeholders', []):
                self.console.print(f"  • {sh['name']} ({sh['stakeholder_type']})")
                self.console.print(f"    Criticality: {sh.get('criticality', 'N/A')}")
                needs = sh.get('mission_perspective', {}).get('primary_needs', [])
                if needs:
                    self.console.print(f"    Primary needs: {', '.join(needs)}")
            
            # Adversaries
            self.console.print("\n[bold]Adversaries:[/bold]")
            for adv in stakeholder_results.get('adversaries', []):
                profile = adv['profile']
                self.console.print(f"  • {adv['adversary_class'].replace('_', ' ').title()}")
                self.console.print(f"    Sophistication: {profile['sophistication']}, Resources: {profile['resources']}")
                self.console.print(f"    Primary interest: {profile['primary_interest']}")
                targets = adv.get('mission_targets', {}).get('interested_in', [])
                if targets:
                    self.console.print(f"    Targets: {', '.join(targets)}")
        
        # Create summary table at the end
        table = Table(title="Analysis Summary", show_header=True)
        table.add_column("Component", style="cyan", width=25)
        table.add_column("Count", justify="right", style="green")
        
        # Add counts to table
        if loss_results:
            loss_count = loss_results.get('loss_count', 0)
            table.add_row("Losses Identified", str(loss_count))
        
        if hazard_results:
            hazard_count = hazard_results.get('hazard_count', 0)
            table.add_row("Hazards Identified", str(hazard_count))
        
        if constraint_results:
            constraint_count = constraint_results.get('constraint_count', 0)
            table.add_row("Security Constraints", str(constraint_count))
        
        if boundary_results:
            boundary_count = len(boundary_results.get('system_boundaries', []))
            table.add_row("System Boundaries", str(boundary_count))
        
        if stakeholder_results:
            # Try both possible count fields
            stakeholder_count = stakeholder_results.get('stakeholder_count', len(stakeholder_results.get('stakeholders', [])))
            adversary_count = stakeholder_results.get('adversary_count', len(stakeholder_results.get('adversaries', [])))
            table.add_row("Stakeholders Identified", str(stakeholder_count))
            table.add_row("Adversaries Profiled", str(adversary_count))
        
        self.console.print("\n")
        self.console.print(table)
        
        # Show cognitive synthesis info if enhanced mode
        if execution_mode != 'standard' and 'cognitive_synthesis' in loss_results:
            synthesis = loss_results['cognitive_synthesis']
            panel = Panel(
                f"Cognitive Styles Used: {', '.join(synthesis['styles_used'])}\n"
                f"Synthesis Method: {synthesis['synthesis_method']}",
                title="ASI-ARCH Dream Team Analysis"
            )
            self.console.print(panel)
    
    
    def _display_completeness_check(self, completeness: dict):
        """Display completeness check results"""
        
        # Create completeness table
        table = Table(title="Analysis Completeness Check")
        table.add_column("Artifact", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Issues", style="yellow")
        
        # Add rows for each artifact
        for artifact_name, status in completeness.get('artifact_status', {}).items():
            status_icon = "✓" if status['complete'] else "✗"
            status_text = "Complete" if status['complete'] else "Incomplete"
            issues = "; ".join(status['issues'][:2]) if status['issues'] else "None"
            if len(status['issues']) > 2:
                issues += f" (+{len(status['issues'])-2} more)"
            
            style = "green" if status['complete'] else "red"
            table.add_row(
                artifact_name.replace('_', ' ').title(),
                f"[{style}]{status_icon} {status_text}[/{style}]",
                issues
            )
        
        self.console.print("\n")
        self.console.print(table)
        
        # Show overall status
        if completeness['is_complete']:
            self.console.print("\n[green]✓ All Step 1 artifacts successfully generated![/green]")
        else:
            self.console.print(f"\n[red]✗ Analysis incomplete: {completeness['summary']}[/red]")
            
            if completeness.get('validation_issues'):
                self.console.print("\n[yellow]Validation Issues:[/yellow]")
                for issue in completeness['validation_issues'][:5]:
                    self.console.print(f"  • {issue}")
                if len(completeness['validation_issues']) > 5:
                    self.console.print(f"  • ...and {len(completeness['validation_issues'])-5} more issues")
    
    def _display_output_files(self):
        """Display information about saved output files"""
        if hasattr(self, '_output_dir') and hasattr(self, '_saved_files'):
            self.console.print("\n[bold]Analysis Output:[/bold]")
            self.console.print(f"Results saved to: {self._output_dir}")
            for file_path in self._saved_files:
                relative_path = file_path.relative_to(Path.cwd()) if file_path.is_relative_to(Path.cwd()) else file_path
                self.console.print(f"  • {relative_path}")
    
    async def _export_database(self, db_name: str, output_dir: Path):
        """Export PostgreSQL database to file"""
        db_host = os.getenv('DB_HOST', 'postgres')
        db_file = output_dir / f"{db_name}.sql"
        
        # Use pg_dump to export the database
        dump_cmd = [
            'pg_dump',
            '-h', db_host,
            '-U', 'sa_user',
            '-d', db_name,
            '-f', str(db_file),
            '--no-password',
            '--verbose'
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = 'sa_password'
        
        try:
            import subprocess
            result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                self.console.print(f"Exported database to: {db_file}")
                self._saved_files.append(db_file)
            else:
                self.console.print(f"[yellow]Warning: Could not export database: {result.stderr}[/yellow]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Database export failed: {e}[/yellow]")
    
    async def _generate_markdown_report(self, config: dict, results: dict, output_dir: Path) -> Optional[Path]:
        """Generate markdown report from analysis results"""
        try:
            report_file = output_dir / 'analysis-report.md'
            
            with open(report_file, 'w') as f:
                # Header
                f.write(f"# Step 1 STPA-Sec Analysis Report\n\n")
                f.write(f"**Analysis Name:** {config['analysis']['name']}\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Execution Mode:** {config.get('execution', {}).get('mode', 'standard')}\n\n")
                
                # Extract results sections
                analysis_results = results.get('results', {})
                mission_results = analysis_results.get('mission_analyst', {})
                loss_results = analysis_results.get('loss_identification', {})
                hazard_results = analysis_results.get('hazard_identification', {})
                constraint_results = analysis_results.get('security_constraints', {})
                boundary_results = analysis_results.get('system_boundaries', {})
                stakeholder_results = analysis_results.get('stakeholder_analyst', {})
                if not stakeholder_results:
                    stakeholder_results = analysis_results.get('stakeholder_analysis', {})
                
                # Mission Statement
                if mission_results:
                    ps = mission_results.get('problem_statement', {})
                    if ps:
                        f.write("## Mission Statement\n\n")
                        f.write(f"**Purpose:** {ps.get('purpose_what', 'N/A')}\n\n")
                        f.write(f"**Method:** {ps.get('method_how', 'N/A')}\n\n")
                        f.write(f"**Goals:** {ps.get('goals_why', 'N/A')}\n\n")
                
                # Losses
                if loss_results:
                    f.write("## Losses\n\n")
                    f.write(f"**Total:** {loss_results.get('loss_count', 0)} losses\n\n")
                    
                    if 'loss_categories' in loss_results:
                        f.write("### Losses by Category\n\n")
                        for category, count in loss_results['loss_categories'].items():
                            f.write(f"- **{category.capitalize()}:** {count}\n")
                        f.write("\n")
                    
                    f.write("### All Losses\n\n")
                    for loss in loss_results.get('losses', []):
                        f.write(f"- **{loss['identifier']}:** {loss['description']}\n")
                        f.write(f"  - Category: {loss['loss_category']}\n")
                        f.write(f"  - Severity: {loss['severity_classification']['magnitude']}\n")
                    f.write("\n")
                
                # Hazards
                if hazard_results:
                    f.write("## Hazards\n\n")
                    f.write(f"**Total:** {hazard_results.get('hazard_count', 0)} hazards\n\n")
                    
                    if 'hazard_categories' in hazard_results:
                        f.write("### Hazards by Category\n\n")
                        for category, count in hazard_results['hazard_categories'].items():
                            f.write(f"- **{category.replace('_', ' ').title()}:** {count}\n")
                        f.write("\n")
                    
                    f.write("### All Hazards\n\n")
                    for hazard in hazard_results.get('hazards', []):
                        f.write(f"- **{hazard['identifier']}:** {hazard['description']}\n")
                        f.write(f"  - Category: {hazard['hazard_category']}\n")
                    f.write("\n")
                
                # Security Constraints
                if constraint_results:
                    f.write("## Security Constraints\n\n")
                    f.write(f"**Total:** {constraint_results.get('constraint_count', 0)} constraints\n\n")
                    
                    if 'constraint_types' in constraint_results:
                        f.write("### Security Constraints by Type\n\n")
                        types = constraint_results['constraint_types']
                        f.write(f"- **Preventive:** {types.get('preventive', 0)}\n")
                        f.write(f"- **Detective:** {types.get('detective', 0)}\n")
                        f.write(f"- **Corrective:** {types.get('corrective', 0)}\n")
                        f.write(f"- **Compensating:** {types.get('compensating', 0)}\n\n")
                    
                    f.write("### All Security Constraints\n\n")
                    for constraint in constraint_results.get('security_constraints', []):
                        f.write(f"- **{constraint['identifier']}:** {constraint['constraint_statement']}\n")
                        f.write(f"  - Type: {constraint['constraint_type']}\n")
                        f.write(f"  - Level: {constraint['enforcement_level']}\n")
                    f.write("\n")
                    
                    f.write("### Constraint-Hazard Mappings\n\n")
                    mappings = constraint_results.get('constraint_hazard_mappings', [])
                    if mappings:
                        for mapping in mappings:
                            f.write(f"- {mapping['constraint_id']} → {mapping['hazard_id']} ({mapping['relationship_type']})\n")
                    else:
                        f.write("No findings\n")
                    f.write("\n")
                
                # System Boundaries
                if boundary_results:
                    f.write("## System Boundaries\n\n")
                    f.write(f"**Total:** {len(boundary_results.get('system_boundaries', []))} boundaries\n\n")
                    
                    f.write("### All System Boundaries\n\n")
                    for boundary in boundary_results.get('system_boundaries', []):
                        f.write(f"- **{boundary['boundary_name']}** ({boundary['boundary_type']})\n")
                        f.write(f"  - {boundary['description']}\n")
                        if 'elements' in boundary:
                            inside = [e for e in boundary['elements'] if e['position'] == 'inside']
                            outside = [e for e in boundary['elements'] if e['position'] == 'outside']
                            interface = [e for e in boundary['elements'] if e['position'] == 'interface']
                            f.write(f"  - Elements: {len(inside)} inside, {len(outside)} outside, {len(interface)} at interface\n")
                    f.write("\n")
                
                # Stakeholders
                if stakeholder_results:
                    f.write("## Stakeholders\n\n")
                    for sh in stakeholder_results.get('stakeholders', []):
                        f.write(f"- **{sh['name']}** ({sh['stakeholder_type']})\n")
                        f.write(f"  - Criticality: {sh.get('criticality', 'N/A')}\n")
                        needs = sh.get('mission_perspective', {}).get('primary_needs', [])
                        if needs:
                            f.write(f"  - Primary needs: {', '.join(needs)}\n")
                    f.write("\n")
                    
                    f.write("## Adversaries\n\n")
                    for adv in stakeholder_results.get('adversaries', []):
                        profile = adv['profile']
                        f.write(f"- **{adv['adversary_class'].replace('_', ' ').title()}**\n")
                        f.write(f"  - Sophistication: {profile['sophistication']}\n")
                        f.write(f"  - Resources: {profile['resources']}\n")
                        f.write(f"  - Primary interest: {profile['primary_interest']}\n")
                        targets = adv.get('mission_targets', {}).get('interested_in', [])
                        if targets:
                            f.write(f"  - Targets: {', '.join(targets)}\n")
                    f.write("\n")
                
                # Analysis Summary
                f.write("## Analysis Summary\n\n")
                f.write("| Component | Count |\n")
                f.write("|-----------|-------|\n")
                
                if loss_results:
                    f.write(f"| Losses Identified | {loss_results.get('loss_count', 0)} |\n")
                if hazard_results:
                    f.write(f"| Hazards Identified | {hazard_results.get('hazard_count', 0)} |\n")
                if constraint_results:
                    f.write(f"| Security Constraints | {constraint_results.get('constraint_count', 0)} |\n")
                if boundary_results:
                    f.write(f"| System Boundaries | {len(boundary_results.get('system_boundaries', []))} |\n")
                if stakeholder_results:
                    stakeholder_count = stakeholder_results.get('stakeholder_count', len(stakeholder_results.get('stakeholders', [])))
                    adversary_count = stakeholder_results.get('adversary_count', len(stakeholder_results.get('adversaries', [])))
                    f.write(f"| Stakeholders Identified | {stakeholder_count} |\n")
                    f.write(f"| Adversaries Profiled | {adversary_count} |\n")
                f.write("\n")
                
                # Completeness Check
                if 'completeness_check' in results:
                    completeness = results['completeness_check']
                    f.write("## Analysis Completeness Check\n\n")
                    f.write("| Artifact | Status | Issues |\n")
                    f.write("|----------|--------|--------|\n")
                    
                    for artifact_name, status in completeness.get('artifact_status', {}).items():
                        status_text = "Complete ✓" if status['complete'] else "Incomplete ✗"
                        issues = "; ".join(status['issues'][:2]) if status['issues'] else "None"
                        if len(status['issues']) > 2:
                            issues += f" (+{len(status['issues'])-2} more)"
                        f.write(f"| {artifact_name.replace('_', ' ').title()} | {status_text} | {issues} |\n")
                    f.write("\n")
                    
                    if completeness['is_complete']:
                        f.write("✓ **All Step 1 artifacts successfully generated!**\n")
                    else:
                        f.write(f"✗ **Analysis incomplete:** {completeness['summary']}\n")
                
            return report_file
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not generate markdown report: {e}[/yellow]")
            return None


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='STPA-Sec Step 1 Analysis CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run Step 1 analysis')
    analyze_parser.add_argument('--config', required=True, help='Configuration file path')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Load pre-packaged demo analysis')
    demo_parser.add_argument('--name', default='banking-analysis', help='Demo name (default: banking-analysis)')
    
    # Export command (future)
    export_parser = subparsers.add_parser('export', help='Export analysis results')
    export_parser.add_argument('--analysis-id', required=True, help='Analysis database name')
    export_parser.add_argument('--format', choices=['json', 'csv', 'markdown'], default='json')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = Step1CLI()
    
    if args.command == 'analyze':
        await cli.analyze(args.config)
    elif args.command == 'demo':
        await cli.demo(args.name)
    elif args.command == 'export':
        # TODO: Implement export functionality
        console.print("[yellow]Export functionality coming soon![/yellow]")


if __name__ == "__main__":
    asyncio.run(main())