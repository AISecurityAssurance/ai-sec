#!/usr/bin/env python3
"""
Test Step 1 Analysis without Docker
This script simulates what the CLI would do but with minimal dependencies
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

# Simple configuration
CONFIG = {
    "analysis_name": "Digital Banking Platform - GPT-4 Turbo Test",
    "system_description_path": "demo/banking-analysis/system-description.txt",
    "output_dir": "analyses/test-gpt4-turbo/",
    "model_provider": "openai",
    "model_name": "gpt-4-turbo-preview",
    "execution_mode": "standard"
}

async def test_analysis():
    """Test the analysis without full CLI setup"""
    
    print("=== STPA-Sec Step 1 Analysis Test ===")
    print(f"Analysis: {CONFIG['analysis_name']}")
    print(f"Model: {CONFIG['model_provider']} - {CONFIG['model_name']}")
    print(f"Mode: {CONFIG['execution_mode']}")
    
    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY not set")
        print("To run a live analysis with GPT-4 Turbo, you need to:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Run this script again: python3 test_analysis.py")
        print("\nFor now, you can:")
        print("- View the demo analysis: python3 cli_demo.py")
        print("- Use a local model with Ollama instead")
        return
    
    # Load system description
    try:
        with open(CONFIG['system_description_path'], 'r') as f:
            system_description = f.read()
        print(f"\n✓ Loaded system description ({len(system_description)} chars)")
    except Exception as e:
        print(f"\n❌ Error loading system description: {e}")
        return
    
    # Create output directory
    output_path = Path(CONFIG['output_dir'])
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created output directory: {output_path}")
    
    # Here we would normally run the full analysis
    # For now, we'll just show what would happen
    print("\n📋 Analysis Steps (what would run):")
    print("1. Mission Analysis - Extract system purpose and goals")
    print("2. Loss Identification - Identify potential losses")
    print("3. Hazard Identification - Identify hazards that could lead to losses")
    print("4. Stakeholder Analysis - Identify stakeholders and adversaries")
    print("5. Security Constraints - Define constraints to prevent hazards")
    print("6. System Boundaries - Define system scope and interfaces")
    print("7. Validation - Validate completeness and consistency")
    
    print("\n📊 Expected Output:")
    print(f"- JSON results: {output_path}/results/")
    print(f"- Markdown report: {output_path}/step1_analysis_report.md")
    print(f"- Analysis log: {output_path}/analysis.log")
    
    print("\n⚠️  Note: To actually run the analysis, we need to:")
    print("1. Set up the full environment with all dependencies")
    print("2. Have a running PostgreSQL database")
    print("3. Use the Docker setup or install all Python dependencies")
    
    # Save a test info file
    test_info = {
        "timestamp": datetime.now().isoformat(),
        "config": CONFIG,
        "status": "test_only",
        "note": "This is a test run showing what would happen"
    }
    
    with open(output_path / "test_info.json", 'w') as f:
        json.dump(test_info, f, indent=2)
    
    print(f"\n✓ Saved test info to: {output_path}/test_info.json")

if __name__ == "__main__":
    asyncio.run(test_analysis())