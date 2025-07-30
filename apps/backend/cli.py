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
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Configure logging BEFORE importing anything that uses SQLAlchemy
# Set up basic config first
logging.basicConfig(level=logging.WARNING, format='%(message)s')

# Suppress noisy loggers
for logger_name in ['sqlalchemy.engine', 'sqlalchemy.engine.Engine', 'httpx', 'asyncio']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Override environment to ensure SQLAlchemy doesn't echo
os.environ['PYTHONUNBUFFERED'] = '1'

import asyncpg
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.status import Status

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agents.step1_agents import Step1Coordinator
from core.database import create_database_pool, run_migrations
from config.settings import settings, ModelProvider, ModelConfig, AuthMethod

console = Console()


class Step1CLI:
    """Command-line interface for STPA-Sec Step 1 analysis"""
    
    def __init__(self):
        # Load .env file - try multiple locations
        # In Docker, we're at /app (backend), project root is /
        # On host, we're at apps/backend, project root is ../..
        possible_env_paths = [
            Path('.env'),  # Current directory
            Path(__file__).parent / '.env',  # Backend directory
            Path(__file__).parent.parent.parent / '.env',  # Project root (host)
            Path('/app/.env'),  # Docker mount point
        ]
        
        for env_path in possible_env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
        
        self.console = console
        self.status = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging to save all logs to a file"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Store log filename for later
        self.log_filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Add file handler to root logger to capture all logs
        file_handler = logging.FileHandler(log_dir / self.log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Add to root logger
        logging.getLogger().addHandler(file_handler)
        
    async def analyze(self, config_path: str, enhanced: bool = False, input_files: List[str] = None):
        """Run Step 1 analysis based on configuration file
        
        Args:
            config_path: Path to configuration file
            enhanced: Whether to use enhanced mode with multiple agents
            input_files: Optional list of input files (overrides config)
        """
        
        # Load configuration
        config = self._load_config(config_path)
        
        # Validate configuration
        self._validate_config(config)
        
        # Set up environment variables for API keys
        self._setup_api_keys(config)
        
        # Test model configuration before creating database
        await self._verify_model_configuration()
        
        # Create analysis database
        db_name, timestamp = await self._create_analysis_database(config)
        
        # Store timestamp for consistent file naming
        self._timestamp = timestamp
        
        # Read system description (only if not using multi-file inputs)
        system_description = ""
        
        # Create progress callback for coordinator
        self.current_phase = "Initializing..."
        
        # Run analysis with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Running Step 1 Analysis - {self.current_phase}", total=None)
            
            try:
                # Connect to database
                db_host = os.getenv('DB_HOST', 'postgres')
                db_url = f"postgresql://sa_user:sa_password@{db_host}:5432/{db_name}"
                db_conn = await asyncpg.connect(db_url)
                
                # Create coordinator with execution mode
                # CLI flag overrides config file setting
                execution_mode = 'enhanced' if enhanced else config.get('execution', {}).get('mode', 'standard')
                coordinator = Step1Coordinator(
                    db_connection=db_conn,
                    execution_mode=execution_mode,
                    db_name=db_name
                )
                
                # Store config file path for resolving relative paths
                self._config_file_path = config_path
                
                # Handle input files from CLI or config
                if input_files:
                    # Use files from command line
                    input_configs = []
                    for file_path in input_files:
                        resolved_path = self._resolve_input_path(file_path, config_path)
                        input_configs.append({
                            'path': str(resolved_path),
                            'type': 'file'  # Auto-detect type
                        })
                else:
                    # Use files from config
                    input_configs = self._get_input_configs_from_config(config, config_path)
                
                # Run analysis with Input Agent
                results = await coordinator.perform_analysis(
                    system_description=system_description,
                    analysis_name=config['analysis']['name'],
                    input_configs=input_configs
                )
                
                # Add model information to results
                model_info = self._get_model_info()
                model_info['execution_mode'] = execution_mode
                results['model_info'] = model_info
                
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
                
                # Add model information to results
                model_info = self._get_model_info()
                model_info['execution_mode'] = "enhanced"  # Demo mode uses enhanced
                results['model_info'] = model_info
                
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
        """Load configuration from YAML file
        
        Attempts to load config from:
        1. Path relative to project root
        2. Absolute path
        3. Fails with clear error
        """
        path = Path(config_path)
        
        # Try as absolute path first
        if path.is_absolute() and path.exists():
            config_file = path
        else:
            # Try multiple locations for relative paths
            # In Docker container, example_systems is mounted at /example_systems
            # On host, it's at project root
            search_paths = []
            
            # If running in Docker (check if /app exists and we're in it)
            if Path('/app').exists() and str(Path(__file__).absolute()).startswith('/app'):
                # Docker environment
                search_paths.extend([
                    Path('/') / config_path,  # Root of container
                    Path('/app').parent / config_path,  # Parent of app dir
                    Path.cwd() / config_path,  # Current directory
                ])
            else:
                # Host environment
                root_dir = Path(__file__).parent.parent.parent
                search_paths.extend([
                    root_dir / config_path,  # Project root
                    Path.cwd() / config_path,  # Current directory
                ])
            
            # Try each path
            config_file = None
            for search_path in search_paths:
                if search_path.exists():
                    config_file = search_path
                    break
            
            if not config_file:
                self.console.print(f"[red]Config file not found: {config_path}[/red]")
                self.console.print(f"[yellow]Searched in:[/yellow]")
                for p in search_paths:
                    self.console.print(f"  - {p}")
                sys.exit(1)
        
        # Store the resolved config file path for later use
        self._resolved_config_path = config_file
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.console.print(f"[green]Loaded config from: {config_file}[/green]")
                return config
        except Exception as e:
            self.console.print(f"[red]Error loading config: {e}[/red]")
            sys.exit(1)
    
    def _resolve_config_path(self, config_path: str) -> Path:
        """Get the resolved config file path"""
        # If we already resolved it during load, return that
        if hasattr(self, '_resolved_config_path'):
            return self._resolved_config_path
        
        # Otherwise resolve it again (shouldn't happen)
        path = Path(config_path)
        if path.is_absolute() and path.exists():
            return path
        
        # Try the same logic as _load_config
        if Path('/app').exists() and str(Path(__file__).absolute()).startswith('/app'):
            # Docker environment
            search_paths = [
                Path('/') / config_path,
                Path('/app').parent / config_path,
                Path.cwd() / config_path,
            ]
        else:
            # Host environment
            root_dir = Path(__file__).parent.parent.parent
            search_paths = [
                root_dir / config_path,
                Path.cwd() / config_path,
            ]
        
        for search_path in search_paths:
            if search_path.exists():
                return search_path
        
        # Default to current directory if not found
        return Path.cwd() / config_path
    
    def _validate_config(self, config: dict):
        """Validate configuration structure"""
        required = ['analysis', 'model', 'input']
        for key in required:
            if key not in config:
                self.console.print(f"[red]Missing required config section: {key}[/red]")
                sys.exit(1)
    
    def _resolve_config_value(self, config: dict, key: str) -> Optional[str]:
        """
        Resolve a config value that can be direct or from env.
        
        Examples:
        - If config has 'model': 'gpt-4' → use 'gpt-4'
        - If config has 'model_env': 'MY_MODEL' → get from env['MY_MODEL']
        - If neither → return None
        """
        # Check for direct value first
        direct_value = config.get(key)
        if direct_value:
            return direct_value
        
        # Check for env reference
        env_key = f"{key}_env"
        env_var_name = config.get(env_key)
        if env_var_name:
            value = os.getenv(env_var_name)
            if not value:
                self.console.print(f"[red]Error: Environment variable '{env_var_name}' not found[/red]")
                self.console.print(f"[yellow]Please set it in your .env file or environment[/yellow]")
                sys.exit(1)
            return value
        
        return None
    
    def _setup_api_keys(self, config: dict):
        """Set up API keys from configuration with explicit resolution"""
        model_config = config.get('model', {})
        
        # Resolve provider (required)
        provider = self._resolve_config_value(model_config, 'provider')
        if not provider:
            self.console.print("[red]Error: Must specify 'provider' or 'provider_env' in model config[/red]")
            sys.exit(1)
        
        # Resolve API key (required for most providers)
        api_key = self._resolve_config_value(model_config, 'api_key')
        
        # Resolve base URL/endpoint (optional)
        base_url = self._resolve_config_value(model_config, 'base_url')
        
        # Resolve model name (required)
        model_name = self._resolve_config_value(model_config, 'name')
        if not model_name:
            model_name = self._resolve_config_value(model_config, 'model')  # Also check 'model' key
            if not model_name:
                self.console.print("[red]Error: Must specify 'name', 'name_env', 'model', or 'model_env' in model config[/red]")
                sys.exit(1)
        
        # Validate required fields based on provider
        if provider != 'ollama' and not api_key:
            self.console.print(f"[red]Error: API key required for provider '{provider}'[/red]")
            self.console.print("[yellow]Please specify 'api_key' or 'api_key_env' in model config[/yellow]")
            sys.exit(1)
        
        # Clear any existing provider config
        if provider in settings.model_providers:
            del settings.model_providers[provider]
        
        # Configure the provider based on type
        if provider == 'openai':
            # Display what we're using
            self.console.print(f"[green]Using OpenAI provider[/green]")
            if base_url:
                self.console.print(f"[dim]  Endpoint: {base_url}[/dim]")
                if 'azure' in base_url.lower():
                    self.console.print("[dim]  (Azure OpenAI detected)[/dim]")
            self.console.print(f"[dim]  Model: {model_name}[/dim]")
            
            settings.model_providers['openai'] = ModelConfig(
                provider=ModelProvider.OPENAI,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                api_endpoint=base_url,
                model=model_name,
                is_enabled=True
            )
            settings.active_provider = ModelProvider.OPENAI
            
        elif provider == 'anthropic':
            self.console.print(f"[green]Using Anthropic provider[/green]")
            self.console.print(f"[dim]  Model: {model_name}[/dim]")
            
            settings.model_providers['anthropic'] = ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                api_endpoint=base_url,
                model=model_name,
                is_enabled=True
            )
            settings.active_provider = ModelProvider.ANTHROPIC
            
        elif provider == 'groq':
            self.console.print(f"[green]Using Groq provider[/green]")
            self.console.print(f"[dim]  Model: {model_name}[/dim]")
            
            settings.model_providers['groq'] = ModelConfig(
                provider=ModelProvider.GROQ,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                api_endpoint=base_url,
                model=model_name,
                is_enabled=True
            )
            settings.active_provider = ModelProvider.GROQ
            
        elif provider == 'ollama':
            # Ollama uses base_url for endpoint
            endpoint = base_url or 'http://localhost:11434'
            self.console.print(f"[green]Using Ollama provider[/green]")
            self.console.print(f"[dim]  Endpoint: {endpoint}[/dim]")
            self.console.print(f"[dim]  Model: {model_name}[/dim]")
            
            settings.model_providers['ollama'] = ModelConfig(
                provider=ModelProvider.OLLAMA,
                auth_method='none',  # Use string value for Ollama
                api_endpoint=endpoint,
                model=model_name,
                is_enabled=True
            )
            settings.active_provider = ModelProvider.OLLAMA
            
        else:
            self.console.print(f"[red]Error: Unknown provider '{provider}'[/red]")
            self.console.print("[yellow]Supported providers: openai, anthropic, groq, ollama[/yellow]")
            sys.exit(1)
        
        # Force reinitialize llm_manager with new settings
        from core.utils.llm_client import llm_manager
        # Clear existing clients first
        llm_manager.clients = {}
        llm_manager._db_checked = False
        llm_manager.reinitialize()
    
    async def _verify_model_configuration(self):
        """Verify that the configured model is available and working"""
        self.console.print("[yellow]Verifying model configuration...[/yellow]")
        
        # Try to get the model client
        try:
            from core.model_providers import get_model_client
            client = get_model_client()
            
            # Do a simple test call
            test_messages = [
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Reply with 'OK' if you receive this."}
            ]
            
            response = await client.generate(test_messages, temperature=0.1, max_tokens=10)
            
            self.console.print(f"[green]✓ Model configuration verified[/green]")
            if settings.active_provider:
                self.console.print(f"[dim]  Provider: {settings.active_provider.value}[/dim]")
            if hasattr(client, 'model'):
                self.console.print(f"[dim]  Model: {client.model}[/dim]")
            if hasattr(client, 'is_azure') and client.is_azure:
                self.console.print(f"[dim]  Type: Azure OpenAI[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]✗ Model configuration failed[/red]")
            self.console.print(f"[red]Error: {str(e)}[/red]")
            
            # Provide helpful error messages
            if "401" in str(e):
                self.console.print("\n[yellow]Authentication failed. Please check:[/yellow]")
                if settings.active_provider == ModelProvider.OPENAI:
                    if 'client' in locals() and hasattr(client, 'is_azure') and client.is_azure:
                        self.console.print("  • AZURE_OPENAI_API_KEY is correct")
                        self.console.print("  • AZURE_OPENAI_API_BASE is the correct endpoint URL")
                        self.console.print("  • AZURE_OPENAI_API_MODEL matches your deployment name")
                    else:
                        self.console.print("  • OPENAI_API_KEY is valid")
            elif "No configuration found" in str(e):
                self.console.print("\n[yellow]No model provider configured. Please set up one of:[/yellow]")
                self.console.print("  • Azure OpenAI: Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_BASE, AZURE_OPENAI_API_MODEL")
                self.console.print("  • OpenAI: Set OPENAI_API_KEY")
                self.console.print("  • Ollama: Install and run Ollama locally")
            
            sys.exit(1)
    
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
    
    def _resolve_input_path(self, input_path: str, config_path: str) -> Path:
        """Resolve input file path relative to config file location
        
        Args:
            input_path: The input file path (relative or absolute)
            config_path: The config file path to use as reference
            
        Returns:
            Resolved absolute path to the input file
        """
        path = Path(input_path)
        
        # If it's already absolute and exists, return it
        if path.is_absolute() and path.exists():
            return path
        
        # Get the config file's directory
        config_file = self._resolve_config_path(config_path)
        config_dir = config_file.parent
        
        # Try paths relative to config file first
        relative_to_config = config_dir / input_path
        if relative_to_config.exists():
            return relative_to_config.resolve()
        
        # Try the same search paths as we use for config files
        if Path('/app').exists() and str(Path(__file__).absolute()).startswith('/app'):
            # Docker environment
            search_paths = [
                Path('/') / input_path,
                Path('/app').parent / input_path,
                Path.cwd() / input_path,
            ]
        else:
            # Host environment
            root_dir = Path(__file__).parent.parent.parent
            search_paths = [
                root_dir / input_path,
                Path.cwd() / input_path,
            ]
        
        for search_path in search_paths:
            if search_path.exists():
                return search_path
        
        # If not found, raise an error
        self.console.print(f"[red]Input file not found: {input_path}[/red]")
        self.console.print(f"[yellow]Searched relative to config: {relative_to_config}[/yellow]")
        self.console.print(f"[yellow]Also searched in:[/yellow]")
        for p in search_paths:
            self.console.print(f"  - {p}")
        sys.exit(1)
    
    def _get_input_configs_from_config(self, config: dict, config_path: str) -> List[Dict[str, Any]]:
        """Extract input configurations from config file
        
        Args:
            config: The parsed configuration dictionary
            config_path: The config file path for resolving relative paths
            
        Returns:
            List of input configurations with resolved paths
        """
        input_configs = []
        input_section = config.get('input', {})
        
        # Check if we have a single input (backward compatibility)
        if 'path' in input_section:
            # Single input file
            resolved_path = self._resolve_input_path(input_section['path'], config_path)
            input_configs.append({
                'path': str(resolved_path),
                'type': input_section.get('type', 'file')
            })
        
        # Check for multiple inputs
        elif 'inputs' in input_section:
            # Multiple input files
            for input_item in input_section['inputs']:
                if isinstance(input_item, str):
                    # Simple string path
                    resolved_path = self._resolve_input_path(input_item, config_path)
                    input_configs.append({
                        'path': str(resolved_path),
                        'type': 'file'
                    })
                elif isinstance(input_item, dict):
                    # Dict with path and optional type
                    resolved_path = self._resolve_input_path(input_item['path'], config_path)
                    input_configs.append({
                        'path': str(resolved_path),
                        'type': input_item.get('type', 'file')
                    })
        
        # If no inputs found and we have the old format, fall back to it
        if not input_configs and 'type' in input_section:
            # This maintains backward compatibility with the old format
            system_desc = self._read_system_description(config)
            # Create a temporary file or use the existing path
            if 'path' in input_section:
                input_configs.append({
                    'path': input_section['path'],
                    'type': 'text',
                    'content': system_desc  # Pass content directly
                })
        
        return input_configs
    
    def _get_model_info(self) -> dict:
        """Get current model configuration info"""
        model_info = {
            "provider": "unknown",
            "model": "unknown",
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        # Find the active provider's config
        active_provider = settings.active_provider
        if active_provider:
            model_info["provider"] = active_provider.value
            
            # Look for the provider's config
            for provider_id, config in settings.model_providers.items():
                if config.provider == active_provider:
                    model_info["model"] = config.model or "default"
                    model_info["temperature"] = config.temperature
                    model_info["max_tokens"] = config.max_tokens
                    # Add Azure indicator if it's Azure OpenAI
                    if config.api_endpoint and config.provider == ModelProvider.OPENAI:
                        model_info["type"] = "Azure OpenAI"
                    break
        
        return model_info
    
    def _read_system_description(self, config: dict) -> str:
        """Read system description from configured source using extensible processors"""
        from analysis.inputs import InputProcessor
        
        processor = InputProcessor()
        
        # Get input configuration
        input_config = config.get('input', {})
        input_type = input_config.get('type', 'file')
        
        if input_type == 'file':
            file_path = input_config.get('path')
            if not file_path:
                self.console.print("[red]No input file specified[/red]")
                sys.exit(1)
            
            # Resolve path (same logic as config)
            path = Path(file_path)
            
            # Try as absolute path first
            if path.is_absolute() and path.exists():
                input_file = path
            else:
                # Try multiple locations for relative paths
                search_paths = []
                
                # If running in Docker
                if Path('/app').exists() and str(Path(__file__).absolute()).startswith('/app'):
                    # Docker environment
                    search_paths.extend([
                        Path('/') / file_path,  # Root of container
                        Path('/app').parent / file_path,  # Parent of app dir
                        Path.cwd() / file_path,  # Current directory
                    ])
                else:
                    # Host environment
                    root_dir = Path(__file__).parent.parent.parent
                    search_paths.extend([
                        root_dir / file_path,  # Project root
                        Path.cwd() / file_path,  # Current directory
                    ])
                
                # Try each path
                input_file = None
                for search_path in search_paths:
                    if search_path.exists():
                        input_file = search_path
                        break
                
                if not input_file:
                    self.console.print(f"[red]Input file not found: {file_path}[/red]")
                    self.console.print(f"[yellow]Searched in:[/yellow]")
                    for p in search_paths:
                        self.console.print(f"  - {p}")
                    sys.exit(1)
            
            try:
                # Use the new input processor
                result = processor.process(str(input_file))
                
                # Display processing info
                input_type_str = result.source_type.value
                self.console.print(f"[green]Loaded {input_type_str} input from: {input_file}[/green]")
                
                # Only show assumptions if they're meaningful (not just restating the obvious)
                if result.assumptions and result.confidence < 0.3:
                    self.console.print("\n[dim]Note: Limited information available for analysis[/dim]\n")
                
                return result.content
                
            except Exception as e:
                self.console.print(f"[red]Error processing input: {e}[/red]")
                sys.exit(1)
        
        elif input_type == 'directory':
            # Handle directory input
            dir_path = input_config.get('path')
            if not dir_path:
                self.console.print("[red]No directory path specified[/red]")
                sys.exit(1)
                
            exclude_patterns = input_config.get('exclude', [])
            
            try:
                result = processor.process(dir_path, exclude=exclude_patterns)
                
                self.console.print(f"[green]Processed directory: {dir_path}[/green]")
                self.console.print(f"[dim]Files analyzed: {len(result.metadata.get('processed_files', []))}[/dim]")
                
                if result.assumptions:
                    self.console.print("\n[yellow]Assumptions:[/yellow]")
                    for assumption in result.assumptions:
                        self.console.print(f"  • {assumption}")
                
                return result.content
                
            except Exception as e:
                self.console.print(f"[red]Error processing directory: {e}[/red]")
                sys.exit(1)
        
        else:
            self.console.print(f"[red]Unsupported input type: {input_type}[/red]")
            sys.exit(1)
    
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
        
        # Save combined results as JSON
        results_file = output_dir / 'analysis-results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Store output info for display
        self._output_dir = output_dir
        self._saved_files = [config_file, results_file]
        
        # Save individual agent results
        individual_files = self._save_individual_results(results, output_dir)
        self._saved_files.extend(individual_files)
        
        # Generate markdown report
        report_file = await self._generate_markdown_report(config, results, output_dir)
        if report_file:
            self._saved_files.append(report_file)
        
        # Export database to the same directory
        await self._export_database(db_name, output_dir)
        
        # Copy log file to artifacts
        if hasattr(self, 'log_filename'):
            log_source = Path("logs") / self.log_filename
            if log_source.exists():
                log_dest = output_dir / "analysis.log"
                import shutil
                shutil.copy2(log_source, log_dest)
                self._saved_files.append(log_dest)
    
    def _display_results_summary(self, results: dict, execution_mode: str):
        """Display detailed analysis results like the demo"""
        
        # Display model information
        model_info = results.get('model_info', {})
        if model_info:
            self.console.print(f"\n[bold cyan]Model Information:[/bold cyan]")
            self.console.print(f"  • Provider: {model_info.get('provider', 'unknown')}")
            self.console.print(f"  • Model: {model_info.get('model', 'unknown')}")
            if 'type' in model_info:
                self.console.print(f"  • Type: {model_info['type']}")
            self.console.print(f"  • Execution Mode: {model_info.get('execution_mode', execution_mode)}")
        
        self.console.print(f"\n[bold green]Step 1 STPA-Sec Analysis Results ({execution_mode} mode)[/bold green]\n")
        
        # Display input summary if available
        input_summary = results.get('input_summary')
        if input_summary and input_summary.get('input_registry'):
            # Show input summary table
            from rich.table import Table
            table = Table(title="Input Analysis Summary")
            table.add_column("Input Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Summary", style="green")
            
            for inp in input_summary['input_registry']:
                table.add_row(
                    inp['filename'],
                    inp['type'].replace('_', ' ').title(),
                    inp['summary']
                )
            
            self.console.print(table)
            self.console.print("")
        
        # Extract results sections
        analysis_results = results.get('results', {})
        mission_results = analysis_results.get('mission_analysis', {})
        loss_results = analysis_results.get('loss_identification', {})
        hazard_results = analysis_results.get('hazard_identification', {})
        constraint_results = analysis_results.get('security_constraints', {})
        boundary_results = analysis_results.get('system_boundaries', {})
        # Get stakeholder results
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
                    
                    # List actual elements, not just counts
                    if inside:
                        self.console.print(f"    INSIDE ({len(inside)}): {', '.join([e['element_name'] for e in inside])}")
                    if outside:
                        self.console.print(f"    OUTSIDE ({len(outside)}): {', '.join([e['element_name'] for e in outside])}")
                    if interface:
                        self.console.print(f"    INTERFACE ({len(interface)}): {', '.join([e['element_name'] for e in interface])}")
        
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
        from rich.table import Table
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
        
        # Analysis Metrics
        self._display_analysis_metrics(analysis_results)
        
        # Critical Findings
        self._display_critical_findings(analysis_results)
    
    
    def _display_completeness_check(self, completeness: dict):
        """Display completeness check results"""
        
        # Create completeness table
        from rich.table import Table
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
            
            # Check if pg_dump exists
            check_cmd = ['which', 'pg_dump']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)
            if check_result.returncode != 0:
                self.console.print("[yellow]Warning: pg_dump not found. Database export skipped.[/yellow]")
                self.console.print("[yellow]To enable database export, rebuild the Docker image with postgresql-client.[/yellow]")
                return
            
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
                f.write(f"**Execution Mode:** {config.get('execution', {}).get('mode', 'standard')}\n")
                
                # Model Information
                model_info = results.get('model_info', {})
                if model_info:
                    f.write(f"\n## Model Information\n\n")
                    f.write(f"- **Provider:** {model_info.get('provider', 'unknown')}\n")
                    f.write(f"- **Model:** {model_info.get('model', 'unknown')}\n")
                    f.write(f"- **Execution Mode:** {model_info.get('execution_mode', 'standard')}\n")
                
                # Input Summary
                input_summary = results.get('input_summary')
                if input_summary and input_summary.get('input_registry'):
                    f.write("## Input Analysis Summary\n\n")
                    f.write("| Input Name | Type | Summary |\n")
                    f.write("|------------|------|---------|\n")
                    
                    for inp in input_summary['input_registry']:
                        f.write(f"| {inp['filename']} | {inp['type'].replace('_', ' ').title()} | "
                               f"{inp['summary']} |\n")
                    f.write("\n")
                
                # Extract results sections
                analysis_results = results.get('results', {})
                mission_results = analysis_results.get('mission_analysis', {})
                loss_results = analysis_results.get('loss_identification', {})
                hazard_results = analysis_results.get('hazard_identification', {})
                constraint_results = analysis_results.get('security_constraints', {})
                boundary_results = analysis_results.get('system_boundaries', {})
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
                            
                            # List actual elements, not just counts
                            if inside:
                                f.write(f"  - **INSIDE ({len(inside)}):** {', '.join([e['element_name'] for e in inside])}\n")
                            if outside:
                                f.write(f"  - **OUTSIDE ({len(outside)}):** {', '.join([e['element_name'] for e in outside])}\n")
                            if interface:
                                f.write(f"  - **INTERFACE ({len(interface)}):** {', '.join([e['element_name'] for e in interface])}\n")
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
    
    def _display_analysis_metrics(self, analysis_results: dict):
        """Display analysis metrics"""
        self.console.print("\n[bold]Analysis Metrics:[/bold]")
        
        # Calculate total findings
        total_findings = 0
        loss_results = analysis_results.get('loss_identification', {})
        hazard_results = analysis_results.get('hazard_identification', {})
        constraint_results = analysis_results.get('security_constraints', {})
        boundary_results = analysis_results.get('system_boundaries', {})
        stakeholder_results = analysis_results.get('stakeholder_analysis', {})
        
        if loss_results:
            total_findings += loss_results.get('loss_count', 0)
            total_findings += len(loss_results.get('dependencies', []))
        if hazard_results:
            total_findings += hazard_results.get('hazard_count', 0)
            total_findings += len(hazard_results.get('hazard_loss_mappings', []))
        if constraint_results:
            total_findings += constraint_results.get('constraint_count', 0)
            total_findings += len(constraint_results.get('constraint_hazard_mappings', []))
        if boundary_results:
            total_findings += len(boundary_results.get('system_boundaries', []))
        if stakeholder_results:
            total_findings += len(stakeholder_results.get('stakeholders', []))
            total_findings += len(stakeholder_results.get('adversaries', []))
        
        self.console.print(f"  • Total findings: {total_findings}")
        self.console.print(f"  • Loss dependencies: {len(loss_results.get('dependencies', []))}")
        self.console.print(f"  • Hazard-loss mappings: {len(hazard_results.get('hazard_loss_mappings', []))}")
        self.console.print(f"  • Security constraints: {constraint_results.get('constraint_count', 0)}")
        self.console.print(f"  • Constraint-hazard mappings: {len(constraint_results.get('constraint_hazard_mappings', []))}")
        self.console.print(f"  • System boundaries: {len(boundary_results.get('system_boundaries', []))}")
    
    def _display_critical_findings(self, analysis_results: dict):
        """Display critical findings"""
        findings = self._generate_critical_findings(analysis_results)
        if findings:
            self.console.print("\n[bold]Critical Findings:[/bold]")
            for i, finding in enumerate(findings, 1):
                self.console.print(f"\n{i}. {finding}")
    
    def _generate_critical_findings(self, results: dict) -> list:
        """Generate critical findings based on analysis patterns"""
        findings = []
        
        # Extract results sections
        loss_results = results.get('loss_identification', {})
        hazard_results = results.get('hazard_identification', {})
        constraint_results = results.get('security_constraints', {})
        stakeholder_results = results.get('stakeholder_analysis', {})
        
        # Helper to get full descriptions
        hazards = {h['identifier']: h for h in hazard_results.get('hazards', [])}
        losses = {l['identifier']: l for l in loss_results.get('losses', [])}
        constraints = {c['identifier']: c for c in constraint_results.get('security_constraints', [])}
        
        # Direct Mappings to Catastrophic Losses
        if hazard_results and loss_results:
            mappings = hazard_results.get('hazard_loss_mappings', [])
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
        
        # Mandatory Constraints Addressing Multiple Hazards
        if constraint_results:
            mappings = constraint_results.get('constraint_hazard_mappings', [])
            constraint_hazard_count = {}
            for mapping in mappings:
                c_id = mapping['constraint_id']
                constraint_hazard_count[c_id] = constraint_hazard_count.get(c_id, 0) + 1
            
            for c_id, count in constraint_hazard_count.items():
                if count > 1:
                    constraint = constraints.get(c_id)
                    if constraint and constraint.get('enforcement_level') == 'mandatory':
                        findings.append(
                            f"[Mandatory Constraint] {c_id} addresses {count} hazard(s)\n"
                            f"  Constraint: {constraint['constraint_statement']}\n"
                            f"  Addresses: {', '.join([m['hazard_id'] for m in mappings if m['constraint_id'] == c_id])}"
                        )
        
        # Dependency Chains
        if loss_results:
            dependencies = loss_results.get('dependencies', [])
            # Look for chains
            for dep1 in dependencies:
                for dep2 in dependencies:
                    if dep1['dependent_loss_id'] == dep2['primary_loss_id']:
                        findings.append(
                            f"[Dependency Chain] {dep1['primary_loss_id']} → {dep1['dependent_loss_id']} → {dep2['dependent_loss_id']}\n"
                            f"  Chain type: {dep1['dependency_type']} → {dep2['dependency_type']}\n"
                            f"  Time relationship: {dep1['time_relationship']['sequence']} → {dep2['time_relationship']['sequence']}"
                        )
        
        # Multiple Hazards to Single Loss
        if hazard_results and loss_results:
            loss_hazard_count = {}
            for mapping in hazard_results.get('hazard_loss_mappings', []):
                l_id = mapping['loss_id']
                if l_id not in loss_hazard_count:
                    loss_hazard_count[l_id] = []
                loss_hazard_count[l_id].append(mapping['hazard_id'])
            
            for l_id, h_ids in loss_hazard_count.items():
                if len(h_ids) >= 3:
                    loss = losses.get(l_id)
                    if loss:
                        hazard_categories = set()
                        for h_id in h_ids[:3]:  # First 3 hazards
                            hazard = hazards.get(h_id)
                            if hazard:
                                hazard_categories.add(hazard.get('hazard_category', 'unknown'))
                        
                        findings.append(
                            f"[Multiple Hazards → Single Loss] {len(h_ids)} hazards target {l_id}\n"
                            f"  Loss: {loss['description']}\n"
                            f"  Hazards: {', '.join(h_ids[:3])} (categories: {', '.join(hazard_categories)})"
                        )
        
        return findings[:10]  # Limit to top 10 findings
    
    def _save_individual_results(self, results: dict, output_dir: Path) -> list:
        """Save individual JSON files for each agent result"""
        saved_files = []
        
        # Create results subdirectory
        results_dir = output_dir / 'results'
        results_dir.mkdir(exist_ok=True)
        
        # Get the analysis results
        analysis_results = results.get('results', {})
        
        # Save each agent's results individually
        agent_files = {
            'mission_analyst': 'mission_analyst.json',
            'loss_identification': 'loss_identification.json',
            'hazard_identification': 'hazard_identification.json',
            'stakeholder_analysis': 'stakeholder_analysis.json',  # Consistent naming
            'security_constraints': 'security_constraints.json',
            'system_boundaries': 'system_boundaries.json',
            'validation': 'validation.json'
        }
        
        for agent_key, filename in agent_files.items():
            if agent_key in analysis_results:
                file_path = results_dir / filename
                # Skip if we already saved this file (e.g., stakeholder_analyst vs stakeholder_analysis)
                if file_path not in saved_files:
                    with open(file_path, 'w') as f:
                        json.dump(analysis_results[agent_key], f, indent=2, default=str)
                    saved_files.append(file_path)
        
        return saved_files


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='STPA-Sec Step 1 Analysis CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run Step 1 analysis')
    analyze_parser.add_argument('--config', required=True, help='Configuration file path')
    analyze_parser.add_argument('--input', nargs='+', help='Input files to analyze (overrides config file)')
    analyze_parser.add_argument('--enhanced', action='store_true', help='Use enhanced mode with multiple agents per phase')
    
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
        await cli.analyze(args.config, enhanced=args.enhanced, input_files=getattr(args, 'input', None))
    elif args.command == 'demo':
        await cli.demo(args.name)
    elif args.command == 'export':
        # TODO: Implement export functionality
        console.print("[yellow]Export functionality coming soon![/yellow]")


if __name__ == "__main__":
    asyncio.run(main())