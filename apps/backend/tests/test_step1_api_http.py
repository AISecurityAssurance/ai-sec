#!/usr/bin/env python3
"""Test Step 1 API endpoints via HTTP only"""
import requests
import json
import time
from datetime import datetime
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

# Test system description
TEST_SYSTEM = """
The Digital Banking Platform is a comprehensive financial services system that enables retail and 
business customers to manage their finances through web and mobile applications. The platform 
provides account management, payment processing, fund transfers, and financial reporting capabilities 
while ensuring regulatory compliance with PCI-DSS, GDPR, and SOX requirements.
"""

def test_step1_workflow():
    """Test the complete Step 1 workflow"""
    
    print("Testing Step 1 API Workflow")
    print("=" * 80)
    
    # 1. First check if API is accessible
    print("\n1. Checking API health...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ API is healthy: {response.json()}")
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("\nMake sure the backend is running:")
        print("  cd apps/backend")
        print("  docker-compose up")
        return
    
    # 2. Create analysis via API
    analysis_id = str(uuid4())
    print(f"\n2. Creating analysis with ID: {analysis_id}")
    
    try:
        # First create the analysis record
        response = requests.post(
            f"{BASE_URL}/stpa-sec/analyses",
            json={
                "name": "Test Banking System Analysis",
                "description": TEST_SYSTEM,
                "system_type": "financial_services"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result['id']
            print(f"✓ Analysis created successfully")
            print(f"  Analysis ID: {analysis_id}")
        else:
            print(f"✗ Failed to create analysis: {response.status_code}")
            print(f"  Response: {response.text}")
            # Try to continue with our generated ID anyway
            
    except Exception as e:
        print(f"  Note: Analysis creation endpoint not available: {e}")
        print(f"  Using generated ID: {analysis_id}")
    
    # 3. Run Step 1 analysis
    print("\n3. Running Step 1 analysis...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/stpa-sec/step1/analyses/{analysis_id}/step1/run",
            json={
                "system_description": TEST_SYSTEM,
                "analysis_name": "Test Banking System Analysis",
                "execution_mode": "standard"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Analysis started successfully")
            print(f"  Analysis ID: {result['analysis_id']}")
            print(f"  Draft ID: {result['draft_id']}")
            print(f"  Status: {result['status']}")
            draft_id = result.get('draft_id')
        else:
            print(f"✗ Failed to start analysis: {response.status_code}")
            print(f"  Response: {response.text}")
            return
            
    except Exception as e:
        print(f"✗ Error calling API: {e}")
        return
    
    # 4. Wait for analysis to complete
    print("\n4. Waiting for analysis to complete...")
    print("  (This may take 10-30 seconds depending on model speed)")
    time.sleep(5)  # Give it time to start
    
    # Poll for completion (in real app, would use WebSocket)
    for i in range(12):  # Try for up to 60 seconds
        time.sleep(5)
        print(f"  Checking status... ({i+1}/12)")
        
        # Check if we have results by checking drafts
        try:
            response = requests.get(
                f"{BASE_URL}/stpa-sec/step1/analyses/{analysis_id}/drafts"
            )
            if response.status_code == 200:
                drafts = response.json()
                if drafts['drafts']:
                    print("  ✓ Analysis appears to be complete")
                    break
        except:
            pass
    
    # 5. Get user drafts
    print("\n5. Getting user drafts...")
    try:
        response = requests.get(
            f"{BASE_URL}/stpa-sec/step1/analyses/{analysis_id}/drafts"
        )
        
        if response.status_code == 200:
            drafts = response.json()
            print(f"✓ Found {len(drafts['drafts'])} draft(s)")
            for draft in drafts['drafts']:
                print(f"  - Draft {draft['id']}: {draft['status']} (edits: {draft.get('edit_count', 0)})")
        else:
            print(f"✗ Failed to get drafts: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error getting drafts: {e}")
    
    # 6. Get versions
    print("\n6. Getting analysis versions...")
    try:
        response = requests.get(
            f"{BASE_URL}/stpa-sec/step1/analyses/{analysis_id}/versions"
        )
        
        if response.status_code == 200:
            versions = response.json()
            print(f"✓ Found {len(versions['versions'])} version(s)")
            for version in versions['versions']:
                print(f"  - Version {version['version_number']}: {version['version_type']}")
        else:
            print(f"✗ Failed to get versions: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error getting versions: {e}")
    
    # 7. Check if analysis data was saved
    print("\n7. Checking if analysis data was saved...")
    try:
        # Try to get the actual analysis data
        response = requests.get(
            f"{BASE_URL}/stpa-sec/analyses/{analysis_id}"
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print("✓ Analysis data retrieved:")
            print(f"  - Name: {analysis.get('name', 'N/A')}")
            print(f"  - Status: {analysis.get('status', 'N/A')}")
            
            # Check for losses
            if 'losses' in analysis:
                print(f"  - Losses: {len(analysis['losses'])}")
            
            # Check for hazards  
            if 'hazards' in analysis:
                print(f"  - Hazards: {len(analysis['hazards'])}")
                
            # Check for stakeholders
            if 'stakeholders' in analysis:
                print(f"  - Stakeholders: {len(analysis['stakeholders'])}")
        else:
            print(f"  Note: Analysis data endpoint returned {response.status_code}")
            
    except Exception as e:
        print(f"  Note: Could not retrieve analysis data: {e}")
    
    print("\n" + "=" * 80)
    print("✓ API workflow test completed!")
    print("\nNote: To see actual analysis results, you can:")
    print("  1. Check the database tables directly")
    print("  2. Use the frontend application")
    print("  3. Check the backend logs for agent execution details")


if __name__ == "__main__":
    test_step1_workflow()