#!/usr/bin/env python3
"""
Test script to verify Ollama integration is working correctly.
"""

import requests
import json
import sys

def test_ollama_connection():
    """Test basic connection to Ollama service."""
    print("🔍 Testing Ollama connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ Successfully connected to Ollama!")
            return True
        else:
            print(f"❌ Failed to connect: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is the service running?")
        print("   Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_model_availability():
    """Test if the required model is available."""
    print("🔍 Checking model availability...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            print(f"📋 Available models: {model_names}")
            
            if "llama3.2:3b" in model_names:
                print("✅ Required model 'llama3.2:3b' is available!")
                return True
            else:
                print("❌ Required model 'llama3.2:3b' not found!")
                print("   Pull the model with: ollama pull llama3.2:3b")
                return False
        else:
            print(f"❌ Failed to get model list: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def test_model_generation():
    """Test if the model can generate responses."""
    print("🔍 Testing model generation...")
    
    try:
        payload = {
            "model": "llama3.2:3b",
            "prompt": "Hello! Please respond with a short greeting.",
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.6,
                "num_predict": 100
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            
            if content and len(content.strip()) > 0:
                print("✅ Model generation successful!")
                print(f"📝 Response: {content[:100]}...")
                return True
            else:
                print("❌ Model generated empty response")
                return False
        else:
            print(f"❌ Generation failed: HTTP {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing generation: {e}")
        return False

def test_fashion_prompt():
    """Test a fashion-specific prompt."""
    print("🔍 Testing fashion analysis prompt...")
    
    try:
        fashion_prompt = """You are a fashion expert. Please provide a brief analysis of what makes a good fashion sense. Keep it under 100 words."""
        
        payload = {
            "model": "llama3.2:3b",
            "prompt": fashion_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.6,
                "num_predict": 200
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            
            if content and len(content.strip()) > 0:
                print("✅ Fashion prompt successful!")
                print(f"📝 Response: {content[:150]}...")
                return True
            else:
                print("❌ Fashion prompt generated empty response")
                return False
        else:
            print(f"❌ Fashion prompt failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fashion prompt: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Ollama Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Connection Test", test_ollama_connection),
        ("Model Availability", test_model_availability),
        ("Basic Generation", test_model_generation),
        ("Fashion Prompt", test_fashion_prompt)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ollama integration is working correctly.")
        print("   You can now run the Style Finder application.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("   Make sure Ollama is running and the model is available.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
