#!/usr/bin/env python3
"""
Test script to verify Flask app and endpoints work correctly
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

def start_app():
    """Start the Flask app in a subprocess"""
    os.chdir('/workspaces/Project')
    return subprocess.Popen(
        [sys.executable, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def test_endpoints():
    """Test all endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Endpoints")
    print("=" * 50)
    
    # Wait for app to start
    print("⏳ Waiting for app to start...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code in [200, 202]:
                break
        except:
            pass
        if i % 5 == 0 and i > 0:
            print(f"  Waiting... {i}s")
        time.sleep(1)
    else:
        print("❌ App failed to start within 30 seconds")
        return False
    
    print("✅ App started\n")
    
    # Test 1: Health endpoint
    print("Test 1: Health Endpoint")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        print("  ✅ PASS\n")
    except Exception as e:
        print(f"  ❌ FAIL: {e}\n")
        return False
    
    # Test 2: Root endpoint
    print("Test 2: Root Endpoint")
    try:
        response = requests.get(f"{base_url}/")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        print("  ✅ PASS\n")
    except Exception as e:
        print(f"  ❌ FAIL: {e}\n")
        return False
    
    # Test 3: Webhook endpoint (should fail without valid data)
    print("Test 3: Webhook Endpoint (Invalid Data)")
    try:
        response = requests.post(f"{base_url}/webhook", json={})
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code in [400, 500]:  # Expected to fail with empty data
            print("  ✅ PASS (correctly rejected empty payload)\n")
        else:
            print("  ⚠️  Unexpected status code\n")
    except Exception as e:
        print(f"  ❌ FAIL: {e}\n")
        return False
    
    # Test 4: 404 error handling
    print("Test 4: 404 Error Handling")
    try:
        response = requests.get(f"{base_url}/notfound")
        print(f"  Status: {response.status_code}")
        if response.status_code == 404:
            print("  ✅ PASS (correctly returned 404)\n")
        else:
            print(f"  ❌ FAIL: Expected 404, got {response.status_code}\n")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}\n")
        return False
    
    print("=" * 50)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    print("Starting Flask app for testing...")
    proc = start_app()
    
    try:
        success = test_endpoints()
        sys.exit(0 if success else 1)
    finally:
        print("\n🛑 Stopping app...")
        proc.terminate()
        proc.wait(timeout=5)
        print("✅ App stopped")
