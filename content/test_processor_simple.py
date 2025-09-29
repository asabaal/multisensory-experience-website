#!/usr/bin/env python3
"""
Simple test of the OpenRouter Qwen3 processor with immediate output
"""

import os
import json
import re
import requests
import sys
import time
from datetime import datetime
from pathlib import Path

def main():
    """Simple test function"""
    print("🚀 Starting OpenRouter Qwen3 Processor Test")
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"🔑 API key found: {api_key[:20]}...")
    
    # Set up paths
    content_dir = Path(__file__).parent
    raw_input_dir = content_dir / "raw-input"
    output_dir = content_dir / "blog" / "published"
    
    print(f"📁 Content dir: {content_dir}")
    print(f"📁 Raw input dir: {raw_input_dir}")
    print(f"📁 Output dir: {output_dir}")
    
    # Find markdown files
    markdown_files = list(raw_input_dir.glob("*.md"))
    print(f"📝 Found {len(markdown_files)} markdown files")
    
    if not markdown_files:
        print("❌ No markdown files found")
        return
    
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
        return
    
    # Load template
    template_path = content_dir / "templates" / "post-template.json"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        print("✅ Loaded template")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    print("🔄 Making API call...")
    
    # Make API call
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model = "qwen/qwen-2.5-coder-32b-instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/asabaal/multisensory-experience-website",
        "X-Title": "Asabaal Ventures Blog Processor Test"
    }
    
    prompt = f"""
Convert the following markdown blog content to structured JSON format.

TEMPLATE STRUCTURE:
```json
{json.dumps(template, indent=2)}
```

MARKDOWN CONTENT:
```markdown
{markdown_content[:1000]}...
```

INSTRUCTIONS:
1. Extract title, create slug, and determine publish date
2. Generate appropriate tags based on content
3. Write a compelling excerpt
4. Set status to "published"
5. Create subtitle and content sections
6. Preserve all markdown formatting in content sections
7. Return ONLY valid JSON - no explanations or additional text

Requirements:
- JSON must be valid and parseable
- All template fields must be present
- Content sections should maintain original structure
- Tags should be relevant and lowercase
- Slug should be URL-friendly
"""
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert blog content processor for Asabaal Ventures. Convert markdown content to structured JSON format following the specified template exactly."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        print(f"📊 API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API call successful!")
            print(f"📝 Response length: {len(content)} characters")
            
            # Try to parse JSON
            try:
                # Clean response
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                else:
                    json_content = content.strip()
                
                result_json = json.loads(json_content)
                print("✅ JSON parsed successfully!")
                
                # Save result
                output_filename = f"{datetime.now().strftime('%Y-%m-%d')}_{first_file.stem}"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / output_filename / "post.json"
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Saved to: {output_path}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response: {content[:500]}...")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("🎉 Test complete!")

if __name__ == "__main__":
    main()