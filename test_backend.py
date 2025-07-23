#!/usr/bin/env python3
"""
Simple backend integration tests
Run with: python test_backend.py
"""
import asyncio
import json
import sys
from typing import Dict, Any
import httpx
import websockets
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
USER_ID = "test-user"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class BackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=30.0)
        self.results = []
        
    async def close(self):
        await self.client.aclose()
    
    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"{status} {name}")
        if details and not passed:
            print(f"  {YELLOW}Details: {details}{RESET}")
        self.results.append((name, passed))
    
    async def test_health(self):
        """Test health endpoint"""
        try:
            response = await self.client.get("/health")
            passed = response.status_code == 200 and response.json()["status"] == "healthy"
            self.log_test("Health check", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health check", False, str(e))
    
    async def test_model_settings(self):
        """Test model settings endpoints"""
        try:
            # Get current settings
            response = await self.client.get("/api/v1/settings/models")
            passed = response.status_code == 200
            self.log_test("Get model settings", passed)
            
            # Check if any provider is configured
            models = response.json()
            has_provider = len(models) > 0
            self.log_test("Model provider configured", has_provider, 
                         f"Found {len(models)} providers")
            
        except Exception as e:
            self.log_test("Model settings", False, str(e))
    
    async def test_analysis_stpa_sec(self):
        """Test STPA-Sec analysis"""
        try:
            payload = {
                "user_id": USER_ID,
                "system_description": "Test e-commerce platform with user authentication",
                "components": ["Web Frontend", "API Gateway", "Auth Service", "Database"],
                "data_flows": [
                    {"from": "Web Frontend", "to": "API Gateway", "data": "User credentials"},
                    {"from": "API Gateway", "to": "Auth Service", "data": "Auth requests"},
                    {"from": "Auth Service", "to": "Database", "data": "User data"}
                ]
            }
            
            response = await self.client.post("/api/v1/analysis/stpa-sec", json=payload)
            passed = response.status_code == 200 and "analysis_id" in response.json()
            self.log_test("STPA-Sec analysis", passed, 
                         f"Status: {response.status_code}")
            
            if passed:
                return response.json()["analysis_id"]
        except Exception as e:
            self.log_test("STPA-Sec analysis", False, str(e))
        return None
    
    async def test_websocket(self, analysis_id: str = None):
        """Test WebSocket connection and updates"""
        try:
            uri = f"{WS_URL}/{USER_ID}"
            async with websockets.connect(uri) as websocket:
                # Connection established
                self.log_test("WebSocket connection", True)
                
                # Wait for any messages (with timeout)
                try:
                    message = await asyncio.wait_for(
                        websocket.recv(), 
                        timeout=5.0
                    )
                    data = json.loads(message)
                    self.log_test("WebSocket message received", True,
                                 f"Type: {data.get('type', 'unknown')}")
                except asyncio.TimeoutError:
                    # No messages within timeout is OK
                    self.log_test("WebSocket ready", True, "No pending messages")
                    
        except Exception as e:
            self.log_test("WebSocket connection", False, str(e))
    
    async def test_all_frameworks(self):
        """Test all security frameworks"""
        frameworks = [
            "stpa-sec", "stride", "pasta", "dread",
            "linddun", "octave", "maestro", "hazop"
        ]
        
        base_payload = {
            "user_id": USER_ID,
            "system_description": "Test system for security analysis",
            "components": ["Component A", "Component B"],
            "data_flows": []
        }
        
        print(f"\n{BLUE}Testing all frameworks:{RESET}")
        for framework in frameworks:
            try:
                response = await self.client.post(
                    f"/api/v1/analysis/{framework}", 
                    json=base_payload
                )
                passed = response.status_code == 200
                self.log_test(f"  {framework.upper()}", passed)
            except Exception as e:
                self.log_test(f"  {framework.upper()}", False, str(e))
    
    async def test_chat(self):
        """Test chat endpoint"""
        try:
            payload = {
                "user_id": USER_ID,
                "message": "What are the main security concerns for a web application?",
                "context": {}
            }
            
            response = await self.client.post("/api/v1/chat", json=payload)
            passed = response.status_code == 200
            self.log_test("Chat endpoint", passed)
            
        except Exception as e:
            self.log_test("Chat endpoint", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for _, p in self.results if p)
        failed = total - passed
        
        print(f"\n{BLUE}{'='*50}{RESET}")
        print(f"{BLUE}Test Summary:{RESET}")
        print(f"  Total:  {total}")
        print(f"  {GREEN}Passed: {passed}{RESET}")
        if failed > 0:
            print(f"  {RED}Failed: {failed}{RESET}")
        print(f"{BLUE}{'='*50}{RESET}")
        
        return failed == 0


async def main():
    """Run all tests"""
    print(f"{BLUE}🧪 Security Analyst Backend Tests{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")
    
    # Check if backend is running
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=2.0)
        if response.status_code != 200:
            raise Exception("Backend not healthy")
    except Exception:
        print(f"{RED}Error: Backend is not running!{RESET}")
        print(f"Please start it with: ./run-backend-local.sh")
        sys.exit(1)
    
    # Run tests
    tester = BackendTester()
    try:
        # Basic tests
        await tester.test_health()
        await tester.test_model_settings()
        
        # Analysis test
        print(f"\n{BLUE}Testing analysis endpoints:{RESET}")
        analysis_id = await tester.test_analysis_stpa_sec()
        
        # WebSocket test
        print(f"\n{BLUE}Testing WebSocket:{RESET}")
        await tester.test_websocket(analysis_id)
        
        # Framework tests
        await tester.test_all_frameworks()
        
        # Chat test
        print(f"\n{BLUE}Testing chat:{RESET}")
        await tester.test_chat()
        
        # Summary
        all_passed = tester.print_summary()
        
    finally:
        await tester.close()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())