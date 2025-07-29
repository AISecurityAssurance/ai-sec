#!/usr/bin/env python3
"""Test that frontend fails properly without database (no fallback to mock data)"""
import subprocess
import time
import requests

def test_frontend_without_backend():
    """Test that frontend shows error when backend is not available"""
    
    print("=== Testing Frontend Behavior Without Backend ===\n")
    
    # First, let's stop the backend if it's running
    print("1. Stopping backend container...")
    subprocess.run(["docker", "stop", "sa_backend"], capture_output=True)
    time.sleep(2)
    
    print("2. Backend stopped. Testing API endpoints...")
    try:
        response = requests.get("http://localhost:8000/api/v1/stpa-sec/losses", timeout=2)
        print("   ❌ Backend is still responding (unexpected)")
    except:
        print("   ✅ Backend is not responding (expected)")
    
    print("\n3. Frontend behavior:")
    print("   - Should show 'Loading analysis data...' briefly")
    print("   - Then show 'Database Connection Failed' error")
    print("   - Should NOT show any mock healthcare data")
    print("   - Should show empty lists if you bypass the error screen")
    
    print("\n4. To verify in browser:")
    print("   a) Open http://localhost:5173")
    print("   b) You should see the error screen with retry button")
    print("   c) Check console - should see 'Failed to load data from API' error")
    print("   d) Should NOT see any healthcare-related data")
    
    input("\nPress Enter after verifying the error screen appears...")
    
    # Restart the backend
    print("\n5. Restarting backend...")
    subprocess.run(["docker", "start", "sa_backend"], capture_output=True)
    time.sleep(5)
    
    # Test that it works again
    print("6. Testing API is back up...")
    try:
        response = requests.get("http://localhost:8000/api/v1/stpa-sec/losses", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is responding again")
            print("\n7. Click 'Retry Connection' button in browser")
            print("   - Should load banking demo data from database")
            print("   - Should NOT show any healthcare mock data")
    except Exception as e:
        print(f"   ❌ Backend failed to restart: {e}")

if __name__ == "__main__":
    test_frontend_without_backend()