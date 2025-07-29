#!/usr/bin/env python3
"""Verify frontend is displaying correct database data"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def get_and_display_data():
    """Get and display the actual data that should appear in frontend"""
    
    print("=== Data That Should Appear in Frontend ===\n")
    
    # Get losses
    losses_response = requests.get(f"{API_BASE}/stpa-sec/losses")
    if losses_response.status_code == 200:
        losses = losses_response.json()
        print("📋 LOSSES (should replace mock 'Health data breach' etc.):")
        for i, loss in enumerate(losses[:3]):  # Show first 3
            print(f"   {i+1}. {loss['description']}")
            print(f"      Type: {loss['impact_type']}, Severity: {loss['severity']}")
        if len(losses) > 3:
            print(f"   ... and {len(losses) - 3} more\n")
    
    # Get hazards
    hazards_response = requests.get(f"{API_BASE}/stpa-sec/hazards")
    if hazards_response.status_code == 200:
        hazards = hazards_response.json()
        print("⚠️  HAZARDS (should replace mock 'Unauthorized access' etc.):")
        for i, hazard in enumerate(hazards[:3]):  # Show first 3
            print(f"   {i+1}. {hazard['description']}")
        if len(hazards) > 3:
            print(f"   ... and {len(hazards) - 3} more\n")
    
    # Get entities
    entities_response = requests.get(f"{API_BASE}/stpa-sec/entities")
    if entities_response.status_code == 200:
        entities = entities_response.json()
        print("🏢 ENTITIES (should replace mock 'Healthcare System' etc.):")
        for entity in entities:
            print(f"   • {entity['name']} ({entity['type']})")
        print()
    
    # Get scenarios
    scenarios_response = requests.get(f"{API_BASE}/stpa-sec/scenarios")
    if scenarios_response.status_code == 200:
        scenarios = scenarios_response.json()
        print("🎯 SCENARIOS:")
        for scenario in scenarios:
            print(f"   • {scenario['description']}")
            print(f"     Impact: {scenario['impact']}, Likelihood: {scenario['likelihood']}")
        print()
    
    print("=== How to Verify in Browser ===")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Look at the Losses tab - should show banking losses, NOT healthcare")
    print("3. Look at the Hazards tab - should show authentication/fraud hazards")
    print("4. Look at the Control Structure - should show banking entities")
    print("5. Check browser console for any errors")
    print("\n✨ The data should automatically load when you open/refresh the page!")

if __name__ == "__main__":
    get_and_display_data()