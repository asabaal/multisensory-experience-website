#!/usr/bin/env python3
"""
Simple demo script to test Qwen 3 Coder model access via OpenRouter API
This makes ONE SIMPLE API call to validate the model works
"""

import os
import requests
import json

def test_qwen3_coder():
    """Test Qwen 3 Coder model with a simple API call"""
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set!")
        return False
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Request payload - SIMPLE TEST
    payload = {
        "model": "qwen/qwen3-coder",  # Qwen 3 Coder model
        "messages": [
            {
                "role": "user",
                "content": "Write a simple Python function that adds two numbers. Keep it brief."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    print("🚀 Testing Qwen 3 Coder model access...")
    print(f"📡 Making API call to OpenRouter...")
    print(f"🤖 Model: {payload['model']}")
    
    try:
        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"💰 Usage info: {result.get('usage', {})}")
            print(f"📝 Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_qwen3_coder()
    if success:
        print("\n🎉 Qwen 3 Coder model is accessible!")
        print("💡 Check your OpenRouter account to confirm the API call was logged.")
    else:
        print("\n💥 Failed to access Qwen 3 Coder model.")
        print("💡 Check your API key and OpenRouter account settings.")