#!/usr/bin/env python3
"""
ConvoTalk Discord Backend API Test Suite
Tests all backend endpoints for the migrated Discord clone application
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://emergent-chat-15.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class ConvoTalkTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.auth_token = None
        self.user_data = None
        self.test_results = []
        
        # Test data - using realistic data as requested
        self.test_user = {
            "username": "alice_cooper",
            "email": "alice.cooper@example.com", 
            "password": "SecurePass123!"
        }
        
        self.test_user_2 = {
            "username": "bob_marley",
            "email": "bob.marley@example.com",
            "password": "ReggaeMusic456!"
        }

    def log_result(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if response_data:
            result["response_data"] = response_data
            
        self.test_results.append(result)
        
        if not success:
            print(f"   Details: {response_data}")

    def test_api_health(self):
        """Test API health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "ConvoTalk API" in data["message"]:
                    self.log_result("API Health Check", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_result("API Health Check", False, "Unexpected response format", data)
                    return False
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_data = data["user"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_result("User Registration", True, f"User registered successfully: {data['user']['username']}")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing token or user in response", data)
                    return False
            elif response.status_code == 400:
                # User might already exist, try login instead
                self.log_result("User Registration", True, "User already exists (expected)", response.json())
                return self.test_user_login()
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False

    def test_user_login(self):
        """Test user login endpoint"""
        try:
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_data = data["user"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_result("User Login", True, f"Login successful: {data['user']['username']}")
                    return True
                else:
                    self.log_result("User Login", False, "Missing token or user in response", data)
                    return False
            else:
                self.log_result("User Login", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("User Login", False, f"Request error: {str(e)}")
            return False

    def test_auth_me(self):
        """Test /auth/me endpoint to verify JWT token"""
        try:
            if not self.auth_token:
                self.log_result("Auth Me", False, "No auth token available")
                return False
                
            response = self.session.get(f"{self.base_url}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "username" in data and "email" in data:
                    self.log_result("Auth Me", True, f"User info retrieved: {data['username']}")
                    return True
                else:
                    self.log_result("Auth Me", False, "Missing user fields in response", data)
                    return False
            else:
                self.log_result("Auth Me", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Auth Me", False, f"Request error: {str(e)}")
            return False

    def test_get_channels(self):
        """Test GET /channels endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Get Channels", False, "No auth token available")
                return False
                
            response = self.session.get(f"{self.base_url}/channels")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Channels", True, f"Retrieved {len(data)} channels")
                    return True
                else:
                    self.log_result("Get Channels", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Channels", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Channels", False, f"Request error: {str(e)}")
            return False

    def test_create_channel(self):
        """Test POST /channels endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Create Channel", False, "No auth token available")
                return False
                
            channel_data = {
                "name": f"test-channel-{int(time.time())}",
                "description": "Test channel created by automated tests",
                "is_private": False
            }
            
            response = self.session.post(
                f"{self.base_url}/channels",
                json=channel_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "name" in data:
                    self.test_channel_id = data["id"]
                    self.log_result("Create Channel", True, f"Channel created: {data['name']}")
                    return True
                else:
                    self.log_result("Create Channel", False, "Missing channel fields in response", data)
                    return False
            else:
                self.log_result("Create Channel", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Channel", False, f"Request error: {str(e)}")
            return False

    def test_send_message(self):
        """Test POST /channels/{channel_id}/messages endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Send Message", False, "No auth token available")
                return False
                
            # Use general channel or created test channel
            channel_id = getattr(self, 'test_channel_id', 'general')
            
            message_data = {
                "content": f"Hello from automated test at {datetime.now().strftime('%H:%M:%S')}!",
                "message_type": "text"
            }
            
            response = self.session.post(
                f"{self.base_url}/channels/{channel_id}/messages",
                json=message_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "content" in data:
                    self.test_message_id = data["id"]
                    self.log_result("Send Message", True, f"Message sent: {data['content'][:50]}...")
                    return True
                else:
                    self.log_result("Send Message", False, "Missing message fields in response", data)
                    return False
            else:
                self.log_result("Send Message", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Send Message", False, f"Request error: {str(e)}")
            return False

    def test_get_messages(self):
        """Test GET /channels/{channel_id}/messages endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Get Messages", False, "No auth token available")
                return False
                
            # Use general channel or created test channel
            channel_id = getattr(self, 'test_channel_id', 'general')
            
            response = self.session.get(f"{self.base_url}/channels/{channel_id}/messages")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Messages", True, f"Retrieved {len(data)} messages from channel")
                    return True
                else:
                    self.log_result("Get Messages", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Messages", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Messages", False, f"Request error: {str(e)}")
            return False

    def test_get_online_users(self):
        """Test GET /users/online endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Get Online Users", False, "No auth token available")
                return False
                
            response = self.session.get(f"{self.base_url}/users/online")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Online Users", True, f"Retrieved {len(data)} online users")
                    return True
                else:
                    self.log_result("Get Online Users", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Online Users", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Online Users", False, f"Request error: {str(e)}")
            return False

    def test_google_oauth(self):
        """Test GET /auth/google endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/auth/google")
            
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data and "emergentagent.com" in data["auth_url"]:
                    self.log_result("Google OAuth", True, f"OAuth URL generated: {data['auth_url']}")
                    return True
                else:
                    self.log_result("Google OAuth", False, "Missing or invalid auth_url in response", data)
                    return False
            else:
                self.log_result("Google OAuth", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Google OAuth", False, f"Request error: {str(e)}")
            return False

    def test_logout(self):
        """Test POST /auth/logout endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Logout", False, "No auth token available")
                return False
                
            response = self.session.post(f"{self.base_url}/auth/logout")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Logout", True, f"Logout successful: {data['message']}")
                    # Clear auth token
                    self.auth_token = None
                    self.session.headers.pop("Authorization", None)
                    return True
                else:
                    self.log_result("Logout", False, "Missing message in response", data)
                    return False
            else:
                self.log_result("Logout", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Logout", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting ConvoTalk Backend API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence following the priority from review request
        tests = [
            ("API Health Check", self.test_api_health),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Auth Me", self.test_auth_me),
            ("Get Channels", self.test_get_channels),
            ("Create Channel", self.test_create_channel),
            ("Send Message", self.test_send_message),
            ("Get Messages", self.test_get_messages),
            ("Get Online Users", self.test_get_online_users),
            ("Google OAuth", self.test_google_oauth),
            ("Logout", self.test_logout)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("=" * 60)
        print(f"📊 Test Results Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

def main():
    """Main test execution"""
    tester = ConvoTalkTester()
    passed, failed, results = tester.run_all_tests()
    
    # Return exit code based on results
    if failed > 0:
        print(f"\n⚠️  {failed} tests failed. Check the details above.")
        sys.exit(1)
    else:
        print(f"\n🎉 All {passed} tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()