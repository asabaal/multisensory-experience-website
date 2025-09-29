#!/usr/bin/env python3
"""
Debug the API response
"""

import os
import json
import requests

def debug_response():
    """Debug the API response"""
    print("🧪 Debugging API response...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model = "qwen/qwen-2.5-coder-32b-instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/asabaal/multisensory-experience-website",
        "X-Title": "Asabaal Ventures Blog Processor Test"
    }
    
    # Simple prompt
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user", 
                "content": "Hello! Please respond with 'Test response' and nothing else."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"📊 Status code: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🔍 Full response: {json.dumps(result, indent=2)}")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"📝 Content: '{content}'")
                print(f"📏 Content length: {len(content)}")
            else:
                print("❌ No choices in response")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_response()