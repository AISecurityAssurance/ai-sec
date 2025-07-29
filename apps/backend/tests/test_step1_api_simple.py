#!/usr/bin/env python3
"""Simple test for Step 1 API endpoints"""
import asyncio
import httpx
import json
import websockets
from datetime import datetime
from uuid import uuid4

BASE_URL = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000/ws"

# Test system description
TEST_SYSTEM = """
The Digital Banking Platform is a comprehensive financial services system that enables retail and 
business customers to manage their finances through web and mobile applications. The platform 
provides account management, payment processing, fund transfers, and financial reporting capabilities 
while ensuring regulatory compliance with PCI-DSS, GDPR, and SOX requirements.
"""

async def test_step1_workflow():
    """Test the complete Step 1 workflow"""
    
    async with httpx.AsyncClient() as client:
        print("Testing Step 1 API Workflow")
        print("=" * 80)
        
        # 1. First create an analysis in the database
        analysis_id = str(uuid4())
        print(f"\n1. Creating analysis with ID: {analysis_id}")
        
        # We need to create the analysis record first
        # For now, we'll assume it exists or create it via SQL
        
        # 2. Run Step 1 analysis
        print("\n2. Running Step 1 analysis...")
        
        # Connect to WebSocket first to receive progress updates
        ws_task = asyncio.create_task(monitor_websocket(f"{analysis_id}"))
        
        # Small delay to ensure WebSocket is connected
        await asyncio.sleep(0.5)
        
        try:
            response = await client.post(
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
                ws_task.cancel()
                return
                
        except Exception as e:
            print(f"✗ Error calling API: {e}")
            ws_task.cancel()
            return
        
        # 3. Wait for analysis to complete (via WebSocket updates)
        print("\n3. Waiting for analysis to complete...")
        await asyncio.sleep(5)  # Give it time to complete
        
        # Cancel WebSocket monitoring
        ws_task.cancel()
        
        # 4. Get user drafts
        print("\n4. Getting user drafts...")
        try:
            response = await client.get(
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
        
        # 5. Get versions
        print("\n5. Getting analysis versions...")
        try:
            response = await client.get(
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
        
        print("\n" + "=" * 80)
        print("✓ API workflow test completed!")
        print("\nNote: To see actual analysis results, check the database tables:")
        print("  - step1_analyses")
        print("  - step1_losses")
        print("  - step1_hazards")
        print("  - step1_stakeholders")


async def monitor_websocket(analysis_id: str):
    """Monitor WebSocket for progress updates"""
    try:
        uri = f"{WS_URL}/analysis_{analysis_id}"
        print(f"\n   Connecting to WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("   ✓ WebSocket connected, monitoring progress...")
            
            # Subscribe to analysis
            await websocket.send(json.dumps({
                "type": "subscribe",
                "analysis_id": analysis_id
            }))
            
            async for message in websocket:
                data = json.loads(message)
                if data['type'] == 'progress':
                    print(f"   Progress: {data['data']['agent']} - {data['data']['status']}")
                elif data['type'] == 'analysis_complete':
                    print(f"   ✓ Analysis completed!")
                    break
                    
    except asyncio.CancelledError:
        print("   WebSocket monitoring stopped")
    except Exception as e:
        print(f"   WebSocket error: {e}")


async def create_test_analysis(analysis_id: str):
    """Create a test analysis record in the database"""
    import asyncpg
    
    DATABASE_URL = "postgresql://sa_user:sa_password@localhost:5432/security_analyst"
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Check if analysis exists
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM step1_analyses WHERE id = $1)",
            analysis_id
        )
        
        if not exists:
            # Create analysis record
            await conn.execute("""
                INSERT INTO step1_analyses (id, name, description, system_type, created_at)
                VALUES ($1, $2, $3, $4, NOW())
            """, analysis_id, "Test Analysis", "Test banking system", "financial_services")
            print(f"✓ Created test analysis record: {analysis_id}")
        else:
            print(f"✓ Analysis already exists: {analysis_id}")
            
    finally:
        await conn.close()


if __name__ == "__main__":
    # First create the test analysis
    analysis_id = str(uuid4())
    asyncio.run(create_test_analysis(analysis_id))
    
    # Then run the workflow test
    asyncio.run(test_step1_workflow())