#!/usr/bin/env python3
"""
OpenRouter Qwen3 Coder Blog Processor
Uses OpenRouter API with Qwen3 Coder model for automated blog processing
"""

import os
import json
import re
import requests
import sys
import time
from datetime import datetime
from pathlib import Path

class OpenRouterQwen3Processor:
    def __init__(self, verbose=True, auto_update=False):
        """Initialize OpenRouter Qwen3 processor
        
        Args:
            verbose: Show detailed timing information
            auto_update: Automatically update existing posts without prompting
        """
        self.verbose = verbose
        self.auto_update = auto_update
        self.max_iterations = 3
        self.start_time = time.time()
        self.content_dir = Path(__file__).parent
        self.raw_input_dir = self.content_dir / "raw-input"
        self.output_dir = self.content_dir / "blog" / "published"
        
        # Ensure directories exist
        self.raw_input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for OpenRouter API key
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            print("❌ OPENROUTER_API_KEY environment variable not set!")
            print("   Please set it with: export OPENROUTER_API_KEY='your-api-key-here'")
            sys.exit(1)
        else:
            print(f"🔑 OpenRouter API key found: {self.api_key[:20]}...")
        
        # OpenRouter configuration
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "qwen/qwen-2.5-coder-32b-instruct"  # Qwen3 Coder model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/asabaal/multisensory-experience-website",
            "X-Title": "Asabaal Ventures Blog Processor"
        }
    
    def log_time(self, message, start_time=None):
        """Log a message with timestamp and duration"""
        if not self.verbose:
            return
        current_time = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')
        if start_time:
            duration = current_time - start_time
            print(f"[{timestamp}] {message} ({duration:.1f}s)")
        else:
            print(f"[{timestamp}] {message}")
    
    def call_qwen3(self, prompt, max_tokens=4000, temperature=0.7):
        """Make API call to Qwen3 via OpenRouter"""
        try:
            payload = {
                "model": self.model,
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
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API call failed: {e}")
            return None
        except KeyError as e:
            print(f"❌ Unexpected API response format: {e}")
            return None
    
    def load_template(self):
        """Load the blog post template"""
        template_path = self.content_dir / "templates" / "post-template.json"
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            return None
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_markdown_file(self, markdown_file):
        """Process a single markdown file"""
        self.log_time(f"Processing {markdown_file.name}")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Load template
        template = self.load_template()
        if not template:
            return False
        
        # Create prompt for Qwen3
        prompt = f"""
Convert the following markdown blog content to structured JSON format.

TEMPLATE STRUCTURE:
```json
{json.dumps(template, indent=2)}
```

MARKDOWN CONTENT:
```markdown
{markdown_content}
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
        
        # Call Qwen3
        self.log_time("Calling Qwen3 Coder API")
        response = self.call_qwen3(prompt, max_tokens=6000, temperature=0.3)
        
        if not response:
            print(f"❌ Failed to get response from Qwen3 for {markdown_file.name}")
            return False
        
        # Extract JSON from response
        try:
            # Clean response - remove markdown code blocks if present
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
            else:
                json_content = response.strip()
            
            # Parse and validate JSON
            result_json = json.loads(json_content)
            
            # Validate required fields
            required_fields = ['metadata', 'content', 'author']
            for field in required_fields:
                if field not in result_json:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create output directory
            output_filename = f"{datetime.now().strftime('%Y-%m-%d')}_{markdown_file.stem}"
            output_dir = self.output_dir / output_filename
            output_dir.mkdir(exist_ok=True)
            
            # Save processed JSON
            output_path = output_dir / "post.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_json, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully processed {markdown_file.name} -> {output_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error for {markdown_file.name}: {e}")
            print(f"Raw response: {response[:500]}...")
            return False
        except Exception as e:
            print(f"❌ Processing error for {markdown_file.name}: {e}")
            return False
    
    def process_all_files(self):
        """Process all markdown files in raw-input directory"""
        self.log_time("Starting OpenRouter Qwen3 processing session")
        
        # Find all markdown files
        markdown_files = list(self.raw_input_dir.glob("*.md"))
        if not markdown_files:
            print("❌ No markdown files found in raw-input directory")
            return
        
        print(f"📝 Found {len(markdown_files)} markdown files to process")
        
        success_count = 0
        for markdown_file in markdown_files:
            if self.process_markdown_file(markdown_file):
                success_count += 1
        
        self.log_time(f"Processing complete", self.start_time)
        print(f"🎯 Results: {success_count}/{len(markdown_files)} files processed successfully")
        
        if success_count == len(markdown_files):
            print("🚀 All files processed successfully!")
        else:
            print("⚠️  Some files failed to process - check error messages above")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process blog posts using OpenRouter Qwen3 Coder')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed timing information')
    parser.add_argument('--auto-update', '-a', action='store_true', help='Auto-update existing posts')
    parser.add_argument('--file', '-f', help='Process specific file only')
    
    args = parser.parse_args()
    
    processor = OpenRouterQwen3Processor(verbose=args.verbose, auto_update=args.auto_update)
    
    if args.file:
        # Process specific file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        processor.process_markdown_file(file_path)
    else:
        # Process all files
        processor.process_all_files()

if __name__ == "__main__":
    main()