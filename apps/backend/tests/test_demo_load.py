#!/usr/bin/env python3
"""
Simple test to verify demo loading works
"""
import json
from pathlib import Path

def test_demo_files():
    """Test that demo files exist and are valid JSON"""
    
    demo_path = Path("demo/banking-analysis")
    print(f"Checking demo at: {demo_path.absolute()}")
    
    # Check directory exists
    if not demo_path.exists():
        print("✗ Demo directory not found")
        return False
        
    print("✓ Demo directory exists")
    
    # Check config file
    config_file = demo_path / "analysis-config.yaml"
    if config_file.exists():
        print("✓ analysis-config.yaml exists")
    else:
        print("✗ analysis-config.yaml missing")
        
    # Check results directory
    results_dir = demo_path / "results"
    if not results_dir.exists():
        print("✗ Results directory not found")
        return False
        
    print("✓ Results directory exists")
    
    # Check each JSON file
    json_files = [
        "mission_analyst.json",
        "loss_identification.json", 
        "hazard_identification.json",
        "stakeholder_analyst.json",
        "validation.json"
    ]
    
    all_valid = True
    for json_file in json_files:
        file_path = results_dir / json_file
        if not file_path.exists():
            print(f"✗ {json_file} missing")
            all_valid = False
            continue
            
        # Try to load and validate JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Basic validation
            if json_file == "mission_analyst.json":
                assert "problem_statement" in data
                assert "mission_context" in data
            elif json_file == "loss_identification.json":
                assert "losses" in data
                assert len(data["losses"]) >= 3
            elif json_file == "hazard_identification.json":
                assert "hazards" in data
                assert len(data["hazards"]) >= 3
            elif json_file == "stakeholder_analyst.json":
                assert "stakeholders" in data
                assert "adversaries" in data
            elif json_file == "validation.json":
                assert "overall_status" in data
                assert "step2_bridge" in data
                
            print(f"✓ {json_file} valid")
            
        except json.JSONDecodeError as e:
            print(f"✗ {json_file} invalid JSON: {e}")
            all_valid = False
        except AssertionError as e:
            print(f"✗ {json_file} missing required fields")
            all_valid = False
        except Exception as e:
            print(f"✗ {json_file} error: {e}")
            all_valid = False
            
    return all_valid


def main():
    """Run demo validation"""
    print("=== Demo Analysis Validation ===\n")
    
    if test_demo_files():
        print("\n✓ Demo analysis is valid and ready to load!")
        print("\nTo load the demo, run:")
        print("  python3 cli.py demo")
    else:
        print("\n✗ Demo analysis has issues - fix them before proceeding")


if __name__ == "__main__":
    main()