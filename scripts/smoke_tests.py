#!/usr/bin/env python3
"""
Smoke tests for production deployment verification.
"""

import argparse
import sys
import time
import requests
from typing import Dict, Any


class SmokeTests:
    """Production smoke tests."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if data.get("status") != "healthy":
                print(f"❌ Health check failed: {data}")
                return False
            
            print("✅ Health endpoint working")
            return True
            
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test root endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code != 200:
                print(f"❌ Root endpoint failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if "Slackbot Content Pipeline" not in data.get("message", ""):
                print(f"❌ Root endpoint unexpected response: {data}")
                return False
            
            print("✅ Root endpoint working")
            return True
            
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints."""
        try:
            # Test batch endpoint with non-existent ID
            response = self.session.get(f"{self.base_url}/api/batches/test-batch-123")
            
            # Should return 404 or proper error response
            if response.status_code not in [404, 500]:
                data = response.json()
                if "error" not in data and "detail" not in data:
                    print(f"❌ API endpoint unexpected response: {data}")
                    return False
            
            print("✅ API endpoints responding correctly")
            return True
            
        except Exception as e:
            print(f"❌ API endpoint error: {e}")
            return False
    
    def test_response_times(self) -> bool:
        """Test response times."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response_time > 5.0:  # 5 second threshold
                print(f"⚠️ Slow response time: {response_time:.2f}s")
                return False
            
            print(f"✅ Response time acceptable: {response_time:.2f}s")
            return True
            
        except Exception as e:
            print(f"❌ Response time test error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all smoke tests."""
        print(f"🔍 Running smoke tests for: {self.base_url}")
        print("=" * 50)
        
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Root Endpoint", self.test_root_endpoint),
            ("API Endpoints", self.test_api_endpoints),
            ("Response Times", self.test_response_times),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        
        print("\n" + "=" * 50)
        print(f"📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All smoke tests passed!")
            return True
        else:
            print("❌ Some smoke tests failed!")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run smoke tests")
    parser.add_argument("--url", required=True, help="Base URL to test")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout")
    
    args = parser.parse_args()
    
    smoke_tests = SmokeTests(args.url)
    smoke_tests.session.timeout = args.timeout
    
    success = smoke_tests.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
