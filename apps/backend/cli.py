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
        db_name = await self._create_analysis_database(config)
        
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
                db_url = f"postgresql://sa_user:sa_password@localhost:5432/{db_name}"
                db_conn = await asyncpg.connect(db_url)
                
                # Create coordinator with execution mode
                execution_mode = config.get('execution', {}).get('mode', 'standard')
                coordinator = Step1Coordinator(
                    db_connection=db_conn,
                    execution_mode=execution_mode
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
        
        # Create analysis database
        db_name = await self._create_analysis_database({'analysis': {'name': f'Demo: {demo_name}'}})
        
        # Display loading message
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Loading demo analysis '{demo_name}'...", total=None)
            
            try:
                # Connect to database
                db_url = f"postgresql://sa_user:sa_password@localhost:5432/{db_name}"
                db_conn = await asyncpg.connect(db_url)
                
                # Create coordinator
                coordinator = Step1Coordinator(
                    db_connection=db_conn,
                    execution_mode="enhanced"  # Demo uses enhanced mode
                )
                
                # Load existing analysis
                results = await coordinator.load_existing_analysis(str(demo_path))
                
                # Display summary
                self._display_results_summary(results, "enhanced")
                
                # Show demo info
                self._display_demo_info(demo_name, results)
                
            finally:
                await db_conn.close()
        
        self.console.print(f"\n✅ Demo loaded! Database: {db_name}")
        self.console.print(f"\n💡 You can now edit this analysis through the web interface or API.")
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
    
    async def _create_analysis_database(self, config: dict) -> str:
        """Create new PostgreSQL database for analysis"""
        # Generate database name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_name = f"stpa_analysis_{timestamp}"
        
        # Create database
        sys_conn = await asyncpg.connect(
            "postgresql://sa_user:sa_password@localhost:5432/postgres"
        )
        
        try:
            await sys_conn.execute(f'CREATE DATABASE "{db_name}"')
            self.console.print(f"Created database: {db_name}")
            
            # Run migrations
            await sys_conn.close()
            db_conn = await asyncpg.connect(
                f"postgresql://sa_user:sa_password@localhost:5432/{db_name}"
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
        
        return db_name
    
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
        output_dir = Path(config['analysis'].get('output_dir', f'./analyses/{db_name}'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration (without secrets)
        config_copy = config.copy()
        if 'model' in config_copy and 'api_key' in config_copy['model']:
            del config_copy['model']['api_key']
        
        with open(output_dir / 'analysis-config.yaml', 'w') as f:
            yaml.dump(config_copy, f)
        
        # Save results as JSON
        with open(output_dir / 'analysis-results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.console.print(f"Results saved to: {output_dir}")
    
    def _display_results_summary(self, results: dict, execution_mode: str):
        """Display summary of analysis results"""
        
        # Create summary table
        table = Table(title=f"Step 1 Analysis Summary ({execution_mode} mode)")
        table.add_column("Component", style="cyan")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Status", style="yellow")
        
        # Extract counts
        loss_results = results['results'].get('loss_identification', {})
        hazard_results = results['results'].get('hazard_identification', {})
        stakeholder_results = results['results'].get('stakeholder_analysis', {})
        
        table.add_row("Losses", str(loss_results.get('loss_count', 0)), "✓")
        table.add_row("Hazards", str(len(hazard_results.get('hazards', []))), "✓")
        table.add_row("Stakeholders", str(len(stakeholder_results.get('stakeholders', []))), "✓")
        
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
    
    def _display_demo_info(self, demo_name: str, results: dict):
        """Display information about the loaded demo"""
        
        # Create info panel
        info_text = [
            f"Demo: {demo_name}",
            f"Analysis ID: {results['analysis_id']}",
            f"Status: {results['status']}",
            "",
            "Key Findings:",
        ]
        
        # Add loss categories
        loss_results = results['results'].get('loss_identification', {})
        if 'loss_categories' in loss_results:
            info_text.append(f"  • Loss Categories: {', '.join(loss_results['loss_categories'].keys())}")
        
        # Add hazard count
        hazard_results = results['results'].get('hazard_identification', {})
        if 'hazard_count' in hazard_results:
            info_text.append(f"  • Hazards Identified: {hazard_results['hazard_count']}")
        
        # Add adversary types
        stakeholder_results = results['results'].get('stakeholder_analysis', {})
        if 'adversaries' in stakeholder_results:
            adversary_types = [a['adversary_class'] for a in stakeholder_results['adversaries']]
            info_text.append(f"  • Adversary Types: {', '.join(adversary_types)}")
        
        panel = Panel(
            "\n".join(info_text),
            title="Demo Analysis Loaded",
            border_style="green"
        )
        self.console.print("\n")
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