#!/usr/bin/env python3
"""
Simple API test for OpenRouter
"""

import os
import requests
import json

def test_api_call():
    """Test a simple API call"""
    print("🧪 Testing OpenRouter API call...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return False
    
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model = "qwen/qwen-2.5-coder-32b-instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/asabaal/multisensory-experience-website",
        "X-Title": "Asabaal Ventures Blog Processor Test"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello! Please respond with just 'API test successful!'"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print("🔄 Making API call...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API call successful!")
            print(f"📝 Response: {content}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ API call timed out")
        return False
    except Exception as e:
        print(f"❌ API call error: {e}")
        return False

if __name__ == "__main__":
    if test_api_call():
        print("\n🎉 API test passed!")
    else:
        print("\n❌ API test failed!")