#!/usr/bin/env python3
"""
Test OpenRouter API connection with Qwen3 Coder model
"""

import os
import requests
import json
import sys

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set!")
        print("   Please set it with: export OPENROUTER_API_KEY='your-api-key-here'")
        return False
    
    print(f"🔑 API key found: {api_key[:20]}...")
    
    # OpenRouter configuration
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model = "qwen/qwen-2.5-coder-32b-instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/asabaal/multisensory-experience-website",
        "X-Title": "Asabaal Ventures Blog Processor Test"
    }
    
    # Test prompt
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant for testing API connections."
            },
            {
                "role": "user",
                "content": "Hello! Please respond with 'OpenRouter connection successful!' and include the current model name."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("🔄 Testing OpenRouter API connection...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        print("✅ OpenRouter connection successful!")
        print(f"📝 Response: {content}")
        print(f"🤖 Model used: {model}")
        print(f"📊 Usage: {result.get('usage', {})}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text[:500]}")
        return False
    except KeyError as e:
        print(f"❌ Unexpected API response format: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing OpenRouter Qwen3 Coder Connection")
    print("=" * 50)
    
    if test_openrouter_connection():
        print("\n🎉 All tests passed! OpenRouter is ready for blog processing.")
        print("\nNext steps:")
        print("1. Set OPENROUTER_API_KEY environment variable")
        print("2. Run: python content/openrouter_qwen3_processor.py")
        print("3. Place markdown files in content/raw-input/ directory")
    else:
        print("\n❌ Connection test failed. Please check your API key and network connection.")
        sys.exit(1)

if __name__ == "__main__":
    main()