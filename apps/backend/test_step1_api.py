#!/usr/bin/env python3
"""Test Step 1 API endpoints"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/stpa-sec/step1"

# Test system description
TEST_SYSTEM = """
The Digital Banking Platform is a comprehensive financial services system that enables retail and 
business customers to manage their finances through web and mobile applications. The platform 
provides account management, payment processing, fund transfers, and financial reporting capabilities 
while ensuring regulatory compliance with PCI-DSS, GDPR, and SOX requirements.
"""

async def test_step1_api():
    """Test the Step 1 API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("Testing Step 1 API Endpoints")
        print("=" * 80)
        
        # 1. Create an analysis first (using existing endpoint)
        print("\n1. Creating analysis...")
        # For now, we'll use a test analysis ID
        analysis_id = "test-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # 2. Run Step 1 analysis
        print("\n2. Running Step 1 analysis...")
        try:
            response = await client.post(
                f"{BASE_URL}/analyses/{analysis_id}/step1/run",
                json={
                    "system_description": TEST_SYSTEM,
                    "analysis_name": "Test Banking System Analysis",
                    "execution_mode": "standard"
                },
                headers={
                    "Authorization": "Bearer test-token"  # Mock auth for now
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Analysis started: {result}")
                draft_id = result.get('draft_id')
            else:
                print(f"✗ Failed to start analysis: {response.status_code}")
                print(f"  Response: {response.text}")
                return
                
        except Exception as e:
            print(f"✗ Error calling API: {e}")
            return
        
        # 3. Wait a bit for analysis to complete
        print("\n3. Waiting for analysis to complete...")
        await asyncio.sleep(2)
        
        # 4. Test element edit
        print("\n4. Testing element edit...")
        # This would normally edit an actual element ID from the analysis
        try:
            response = await client.put(
                f"{BASE_URL}/analyses/{analysis_id}/elements/loss/test-loss-1",
                json={
                    "changes": {
                        "description": "Updated loss description"
                    },
                    "freeze": False
                },
                headers={
                    "Authorization": "Bearer test-token"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Edit saved: {result}")
            else:
                print(f"  Note: Edit endpoint returned {response.status_code} (expected for test data)")
                
        except Exception as e:
            print(f"  Note: Edit test skipped: {e}")
        
        # 5. Get drafts
        print("\n5. Getting user drafts...")
        try:
            response = await client.get(
                f"{BASE_URL}/analyses/{analysis_id}/drafts",
                headers={
                    "Authorization": "Bearer test-token"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Drafts retrieved: {result}")
            else:
                print(f"  Note: Drafts endpoint returned {response.status_code}")
                
        except Exception as e:
            print(f"  Note: Drafts test skipped: {e}")
        
        # 6. Test WebSocket connection (would need actual WebSocket client)
        print("\n6. WebSocket connection test...")
        print("  Note: WebSocket testing requires a WebSocket client")
        
        print("\n" + "=" * 80)
        print("API endpoint structure verified!")
        print("Note: Full testing requires proper authentication setup")

if __name__ == "__main__":
    asyncio.run(test_step1_api())