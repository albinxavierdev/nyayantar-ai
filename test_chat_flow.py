#!/usr/bin/env python3
"""
Comprehensive Chat Flow Test Script
Tests the complete RAG chat flow from UI to database
"""

import asyncio
import json
import sys
import os
import requests
from datetime import datetime

# Add backend to path
sys.path.append('backend')

# Test configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class ChatFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.conversation_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_backend_health(self):
        """Test if backend is running and healthy"""
        try:
            response = self.session.get(f"{BASE_URL}/docs", timeout=5)
            success = response.status_code == 200
            self.log_test("Backend Health Check", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False
    
    def test_database_connection(self):
        """Test database connection through backend"""
        try:
            # This would require a health endpoint that checks DB
            # For now, we'll test by trying to create a conversation
            response = self.session.get(f"{BASE_URL}/api/conversation/", timeout=5)
            success = response.status_code in [200, 401]  # 401 means auth required, which is expected
            self.log_test("Database Connection", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    def test_authentication_flow(self):
        """Test authentication endpoints"""
        try:
            # Test signup endpoint
            signup_data = {
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/signup", 
                                       json=signup_data, timeout=10)
            success = response.status_code in [200, 201, 400]  # 400 might mean user exists
            self.log_test("Authentication Signup", success, 
                         f"Status: {response.status_code}")
            
            # Test signin endpoint
            signin_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/signin", 
                                       json=signin_data, timeout=10)
            success = response.status_code in [200, 401]  # 401 if user doesn't exist
            self.log_test("Authentication Signin", success, 
                         f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.log_test("Token Extraction", bool(self.access_token), 
                             "Access token extracted" if self.access_token else "No token found")
            
            return success
        except Exception as e:
            self.log_test("Authentication Flow", False, str(e))
            return False
    
    def test_conversation_management(self):
        """Test conversation creation and management"""
        if not self.access_token:
            self.log_test("Conversation Management", False, "No access token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Test conversation creation
            response = self.session.get(f"{BASE_URL}/api/conversation/", 
                                      headers=headers, timeout=10)
            success = response.status_code == 200
            self.log_test("Conversation Creation", success, 
                         f"Status: {response.status_code}")
            
            if success:
                data = response.json()
                self.conversation_id = data.get("conversation_id")
                self.log_test("Conversation ID Extraction", bool(self.conversation_id), 
                             "Conversation ID extracted" if self.conversation_id else "No ID found")
            
            # Test conversation list
            response = self.session.get(f"{BASE_URL}/api/conversation/list", 
                                      headers=headers, timeout=10)
            success = response.status_code == 200
            self.log_test("Conversation List", success, 
                         f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Conversation Management", False, str(e))
            return False
    
    def test_chat_endpoint(self):
        """Test the main chat endpoint"""
        if not self.access_token or not self.conversation_id:
            self.log_test("Chat Endpoint", False, "Missing token or conversation ID")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            chat_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test message"
                    }
                ],
                "data": {}
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/chat?conversation_id={self.conversation_id}",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            self.log_test("Chat Endpoint", success, 
                         f"Status: {response.status_code}")
            
            if success:
                # Check if response is streaming
                content_type = response.headers.get("content-type", "")
                is_streaming = "text/event-stream" in content_type or "text/plain" in content_type
                self.log_test("Streaming Response", is_streaming, 
                             f"Content-Type: {content_type}")
            
            return success
        except Exception as e:
            self.log_test("Chat Endpoint", False, str(e))
            return False
    
    def test_legal_chat_endpoint(self):
        """Test the legal chat endpoint"""
        if not self.access_token:
            self.log_test("Legal Chat Endpoint", False, "No access token")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            legal_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the legal requirements for starting a business in India?"
                    }
                ]
            }
            
            response = self.session.post(f"{BASE_URL}/api/legal", 
                                       json=legal_data, headers=headers, timeout=30)
            
            success = response.status_code == 200
            self.log_test("Legal Chat Endpoint", success, 
                         f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Legal Chat Endpoint", False, str(e))
            return False
    
    def test_frontend_build(self):
        """Test if frontend builds successfully"""
        try:
            import subprocess
            result = subprocess.run(
                ["npm", "run", "build", "--dry-run"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            self.log_test("Frontend Build", success, 
                         f"Return code: {result.returncode}")
            
            if not success:
                self.log_test("Frontend Build Error", False, result.stderr[:200])
            
            return success
        except Exception as e:
            self.log_test("Frontend Build", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Chat Flow Test")
        print("=" * 50)
        
        # Backend tests
        print("\n📡 Backend Tests")
        print("-" * 20)
        self.test_backend_health()
        self.test_database_connection()
        
        # Authentication tests
        print("\n🔐 Authentication Tests")
        print("-" * 25)
        self.test_authentication_flow()
        
        # Chat functionality tests
        print("\n💬 Chat Functionality Tests")
        print("-" * 30)
        self.test_conversation_management()
        self.test_chat_endpoint()
        self.test_legal_chat_endpoint()
        
        # Frontend tests
        print("\n🎨 Frontend Tests")
        print("-" * 18)
        self.test_frontend_build()
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Save results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to test_results.json")
        
        return passed == total

def main():
    """Main function"""
    tester = ChatFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Chat flow is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
