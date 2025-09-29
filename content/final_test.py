#!/usr/bin/env python3
"""
Final test of OpenRouter Qwen3 processor with proper response handling
"""

import os
import json
import re
import requests
import time
from datetime import datetime
from pathlib import Path

def extract_json_from_response(response_text):
    """Extract JSON from API response text"""
    # Try to find JSON in code blocks first
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    
    # Try to find JSON object directly
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        return json_match.group(0).strip()
    
    # If no JSON found, return the original text
    return response_text.strip()

def test_blog_processing():
    """Test blog processing with proper response handling"""
    print("🚀 Starting Final Blog Processing Test")
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"🔑 API key found: {api_key[:20]}...")
    
    # Set up paths
    content_dir = Path(__file__).parent
    raw_input_dir = content_dir / "raw-input"
    output_dir = content_dir / "blog" / "published"
    
    # Find markdown files
    markdown_files = list(raw_input_dir.glob("*.md"))
    print(f"📝 Found {len(markdown_files)} markdown files")
    
    if not markdown_files:
        print("❌ No markdown files found")
        return False
    
    # Process first file only for testing
    first_file = markdown_files[0]
    print(f"📄 Processing: {first_file.name}")
    
    # Read the file
    try:
        with open(first_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        print(f"✅ Read file ({len(markdown_content)} characters)")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Load template
    template_path = content_dir / "templates" / "post-template.json"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        print("✅ Loaded template")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return False
    
    # Make API call
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model = "qwen/qwen-2.5-coder-32b-instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/asabaal/multisensory-experience-website",
        "X-Title": "Asabaal Ventures Blog Processor"
    }
    
    # Create a simpler prompt for testing
    prompt = f"""
Convert this blog content to JSON format:

TITLE: More Than Me: How My Beliefs Evolved

CONTENT:
{markdown_content[:2000]}...

Return ONLY valid JSON in this format:
{{
  "metadata": {{
    "title": "More Than Me: How My Beliefs Evolved",
    "slug": "more-than-me-how-my-beliefs-evolved",
    "publishDate": "2024-08-19",
    "tags": ["personal-growth", "beliefs", "evolution"],
    "excerpt": "A brief excerpt about the evolution of beliefs...",
    "coverImage": "cover.jpg",
    "featured": false,
    "status": "published"
  }},
  "content": {{
    "subtitle": "A journey of personal transformation",
    "sections": [
      {{
        "type": "intro",
        "content": {{
          "text": "Introduction text here..."
        }},
        "order": 1
      }}
    ]
  }},
  "author": {{
    "name": "Asabaal Horan",
    "signature": "In love and unity,<br><strong>Asabaal Horan</strong><br>Founder, Asabaal Ventures"
  }}
}}

Return ONLY the JSON, no other text.
"""
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a JSON generator. Return ONLY valid JSON, no explanations or other text."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.1
    }
    
    try:
        print("🔄 Making API call...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        print(f"📊 API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API call successful!")
            print(f"📝 Raw response length: {len(content)} characters")
            
            # Extract JSON from response
            json_content = extract_json_from_response(content)
            print(f"📋 Extracted JSON length: {len(json_content)} characters")
            
            # Try to parse JSON
            try:
                result_json = json.loads(json_content)
                print("✅ JSON parsed successfully!")
                
                # Validate required fields
                required_fields = ['metadata', 'content', 'author']
                for field in required_fields:
                    if field not in result_json:
                        print(f"❌ Missing required field: {field}")
                        return False
                
                # Save result
                output_filename = f"{datetime.now().strftime('%Y-%m-%d')}_{first_file.stem}"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / output_filename / "post.json"
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Saved to: {output_path}")
                print("🎉 Blog processing test successful!")
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Extracted JSON: {json_content[:1000]}...")
                return False
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_blog_processing()
    if success:
        print("\n🎉 All tests passed! OpenRouter Qwen3 processor is working correctly.")
    else:
        print("\n❌ Test failed. Check the error messages above.")