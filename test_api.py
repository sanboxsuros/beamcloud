#!/usr/bin/env python3
"""
Test script for Beam vLLM API
Tests the OpenAI-compatible endpoints after deployment
"""

import requests
import json
import time
import sys
from typing import Optional

class BeamVLLMTester:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or "dummy"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def test_health(self):
        """Test the health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_models(self):
        """Test the models endpoint"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", headers=self.headers)
            if response.status_code == 200:
                models = response.json()
                print("✅ Models endpoint working")
                print(f"   Available models: {[m['id'] for m in models['data']]}")
                return True
            else:
                print(f"❌ Models endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Models endpoint error: {str(e)}")
            return False
    
    def test_chat_completion(self, message: str = "Hello! How are you today?"):
        """Test chat completion endpoint"""
        try:
            payload = {
                "model": "microsoft/DialoGPT-medium",
                "messages": [
                    {"role": "user", "content": message}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print(f"🧪 Testing chat completion with: '{message}'")
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
                print("✅ Chat completion successful")
                print(f"   Model: {result['model']}")
                print(f"   Response: {reply}")
                print(f"   Tokens used: {result['usage']['total_tokens']}")
                return True
            else:
                print(f"❌ Chat completion failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chat completion error: {str(e)}")
            return False
    
    def test_completion(self, prompt: str = "The future of AI is"):
        """Test text completion endpoint"""
        try:
            payload = {
                "model": "microsoft/DialoGPT-medium",
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print(f"🧪 Testing completion with prompt: '{prompt}'")
            response = requests.post(
                f"{self.base_url}/v1/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                completion = result["choices"][0]["text"]
                print("✅ Text completion successful")
                print(f"   Model: {result['model']}")
                print(f"   Completion: {completion}")
                print(f"   Tokens used: {result['usage']['total_tokens']}")
                return True
            else:
                print(f"❌ Text completion failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Text completion error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all available tests"""
        print(f"🚀 Testing Beam vLLM API at: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Models Endpoint", self.test_models),
            ("Chat Completion", self.test_chat_completion),
            ("Text Completion", self.test_completion)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name}...")
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<20} {status}")
            if result:
                passed += 1
        
        print(f"\nPassed: {passed}/{len(results)} tests")
        
        if passed == len(results):
            print("🎉 All tests passed! Your vLLM API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the errors above.")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <beam_endpoint_url>")
        print("Example: python test_api.py https://abc123-8888.app.beam.cloud")
        sys.exit(1)
    
    endpoint_url = sys.argv[1]
    
    # Remove trailing slash if present
    if endpoint_url.endswith('/'):
        endpoint_url = endpoint_url[:-1]
    
    # Run tests
    tester = BeamVLLMTester(endpoint_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()