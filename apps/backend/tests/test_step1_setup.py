#!/usr/bin/env python3
"""
Test script to verify Step 1 analysis setup
"""
import asyncio
import os
import sys
import asyncpg
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings, ModelProvider, ModelConfig
from core.model_providers import get_model_client


async def test_database_connection():
    """Test database connectivity"""
    print("Testing database connection...")
    try:
        # Test connection to main postgres database
        conn = await asyncpg.connect(
            "postgresql://sa_user:sa_password@localhost:5432/postgres"
        )
        version = await conn.fetchval("SELECT version()")
        print(f"✓ PostgreSQL connected: {version.split(',')[0]}")
        
        # Test creating a test database
        test_db = "test_step1_setup"
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{test_db}"')
            await conn.execute(f'CREATE DATABASE "{test_db}"')
            print(f"✓ Can create databases: {test_db}")
            await conn.execute(f'DROP DATABASE "{test_db}"')
        except Exception as e:
            print(f"✗ Database creation failed: {e}")
            
        await conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def test_model_providers():
    """Test model provider connectivity"""
    print("\nTesting model providers...")
    
    # Test OpenAI if API key is set
    if "OPENAI_API_KEY" in os.environ:
        print("Testing OpenAI...")
        try:
            settings.model_providers['openai'] = ModelConfig(
                provider=ModelProvider.OPENAI,
                auth_method='api-key',
                api_key=os.environ["OPENAI_API_KEY"],
                model='gpt-4-turbo-preview',
                is_enabled=True
            )
            settings.active_provider = ModelProvider.OPENAI
            
            client = get_model_client()
            response = await client.generate(
                messages=[{"role": "user", "content": "Say 'OpenAI connected' in 3 words"}],
                temperature=0
            )
            print(f"✓ OpenAI connected: {response.content.strip()}")
        except Exception as e:
            print(f"✗ OpenAI failed: {e}")
    else:
        print("⚠ OPENAI_API_KEY not set - skipping OpenAI test")
    
    # Test Ollama
    print("\nTesting Ollama...")
    try:
        settings.model_providers['ollama'] = ModelConfig(
            provider=ModelProvider.OLLAMA,
            auth_method='none',
            api_endpoint='http://localhost:11434',
            model='mixtral:instruct',
            is_enabled=True
        )
        settings.active_provider = ModelProvider.OLLAMA
        
        client = get_model_client()
        response = await client.generate(
            messages=[{"role": "user", "content": "Say 'Ollama connected' in 3 words"}],
            temperature=0
        )
        print(f"✓ Ollama connected: {response.content.strip()}")
    except Exception as e:
        print(f"✗ Ollama failed: {e}")
        print("  Make sure Ollama is running: ollama serve")
        print("  And mixtral:instruct is pulled: ollama pull mixtral:instruct")


def test_file_structure():
    """Test required files and directories exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "demo-banking-system.txt",
        "migrations/001_step1_core_schema.sql",
        "migrations/002_step1_agent_support.sql",
        "demo/banking-analysis/analysis-config.yaml",
        "demo/banking-analysis/results/mission_analyst.json",
        "demo/banking-analysis/results/loss_identification.json",
        "demo/banking-analysis/results/hazard_identification.json",
        "demo/banking-analysis/results/stakeholder_analyst.json",
        "demo/banking-analysis/results/validation.json"
    ]
    
    all_good = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            all_good = False
    
    return all_good


def test_step1_imports():
    """Test Step 1 module imports"""
    print("\nTesting Step 1 imports...")
    
    try:
        from core.agents.step1_agents import Step1Coordinator
        print("✓ Step1Coordinator")
        
        from core.agents.step1_agents import MissionAnalystAgent
        print("✓ MissionAnalystAgent")
        
        from core.agents.step1_agents import LossIdentificationAgent
        print("✓ LossIdentificationAgent")
        
        from core.agents.step1_agents import HazardIdentificationAgent
        print("✓ HazardIdentificationAgent")
        
        from core.agents.step1_agents import StakeholderAnalystAgent
        print("✓ StakeholderAnalystAgent")
        
        from core.agents.step1_agents import ValidationAgent
        print("✓ ValidationAgent")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=== Step 1 Analysis Setup Test ===\n")
    
    # Run tests
    db_ok = await test_database_connection()
    imports_ok = test_step1_imports()
    files_ok = test_file_structure()
    await test_model_providers()
    
    print("\n=== Summary ===")
    if db_ok and imports_ok and files_ok:
        print("✓ System ready for Step 1 analysis!")
        print("\nTo run analysis:")
        print("  Demo mode: python cli.py demo")
        print("  With GPT-4: python cli.py analyze --config configs/test-gpt4-standard.yaml")
        print("  With Ollama: python cli.py analyze --config configs/test-ollama-standard.yaml")
    else:
        print("✗ System not ready - fix issues above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())