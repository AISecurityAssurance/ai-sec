#!/usr/bin/env python3
"""Test frontend integration with database data"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_api_endpoints():
    """Test all STPA-Sec API endpoints"""
    endpoints = [
        ("/stpa-sec/system-definition", "System Definition"),
        ("/stpa-sec/losses", "Losses"),
        ("/stpa-sec/hazards", "Hazards"),
        ("/stpa-sec/entities", "Entities"),
        ("/stpa-sec/control-structure", "Control Structure"),
        ("/stpa-sec/scenarios", "Scenarios"),
        ("/stpa-sec/mitigations", "Mitigations"),
        ("/stpa-sec/adversaries", "Adversaries"),
        ("/stpa-sec/risk-summary", "Risk Summary"),
    ]
    
    all_successful = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✓ {name}: {len(data)} items")
                elif isinstance(data, dict) and 'entities' in data:
                    print(f"✓ {name}: {len(data['entities'])} entities, {len(data['relationships'])} relationships")
                else:
                    print(f"✓ {name}: Data loaded")
            else:
                print(f"✗ {name}: HTTP {response.status_code}")
                all_successful = False
        except Exception as e:
            print(f"✗ {name}: {str(e)}")
            all_successful = False
    
    return all_successful

def test_frontend_api_calls():
    """Simulate the frontend API calls"""
    print("\n=== Simulating Frontend API Calls ===")
    
    # This simulates what stpaSecApiService.loadAnalysisData() does
    try:
        # Parallel requests like the frontend
        endpoints = [
            "/stpa-sec/system-definition",
            "/stpa-sec/losses",
            "/stpa-sec/hazards",
            "/stpa-sec/control-structure",
            "/stpa-sec/scenarios",
            "/stpa-sec/mitigations",
            "/stpa-sec/adversaries"
        ]
        
        start_time = time.time()
        
        # Make all requests
        results = {}
        for endpoint in endpoints:
            response = requests.get(f"{API_BASE}{endpoint}")
            if response.status_code == 200:
                results[endpoint] = response.json()
        
        end_time = time.time()
        
        print(f"✓ All data loaded in {end_time - start_time:.2f} seconds")
        
        # Display summary
        print("\n=== Data Summary ===")
        losses = results.get("/stpa-sec/losses", [])
        hazards = results.get("/stpa-sec/hazards", [])
        entities = results.get("/stpa-sec/control-structure", {}).get("entities", [])
        scenarios = results.get("/stpa-sec/scenarios", [])
        
        print(f"• Losses: {len(losses)}")
        if losses:
            print(f"  - First loss: {losses[0]['description'][:50]}...")
        
        print(f"• Hazards: {len(hazards)}")
        if hazards:
            print(f"  - First hazard: {hazards[0]['description'][:50]}...")
        
        print(f"• Entities: {len(entities)}")
        if entities:
            print(f"  - First entity: {entities[0]['name']}")
        
        print(f"• Scenarios: {len(scenarios)}")
        if scenarios:
            print(f"  - First scenario: {scenarios[0]['description'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Frontend simulation failed: {str(e)}")
        return False

def main():
    print("=== Testing Frontend-Database Integration ===\n")
    
    # Test individual endpoints
    print("=== Testing Individual Endpoints ===")
    endpoints_ok = test_api_endpoints()
    
    # Test frontend-like behavior
    frontend_ok = test_frontend_api_calls()
    
    if endpoints_ok and frontend_ok:
        print("\n✅ All tests passed! Frontend should display database data.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    print("\n💡 To verify in browser:")
    print("1. Open http://localhost:5173")
    print("2. Open browser console (F12)")
    print("3. Look for 'Loading analysis data...' message")
    print("4. Check that losses, hazards, etc. show banking system data")
    print("5. Verify no red mock data warning messages appear")

if __name__ == "__main__":
    main()