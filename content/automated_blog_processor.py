#!/usr/bin/env python3
"""
Automated Blog Processor using Claude Code
Programmatically processes blog posts using Claude Code commands
"""

import os
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class AutomatedBlogProcessor:
    def __init__(self):
        self.content_dir = Path(__file__).parent
        self.raw_input_dir = self.content_dir / "raw-input"
        self.output_dir = self.content_dir / "blog" / "published"
        
    def extract_content_and_assets(self, file_path):
        """Extract content from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled Post"
        
        # Extract assets
        assets_match = re.search(r'## Assets\s*\n(.*?)(?:\n---|\n##|\Z)', content, re.DOTALL)
        assets = {}
        
        if assets_match:
            assets_text = assets_match.group(1)
            
            cover_match = re.search(r'\*\*Cover Image:\*\*\s*(.+)', assets_text)
            if cover_match:
                assets['cover_image'] = cover_match.group(1).strip()
            
            images_match = re.search(r'\*\*Other Images:\*\*\s*(.+)', assets_text)
            if images_match:
                images_text = images_match.group(1).strip()
                if images_text:
                    assets['images'] = [img.strip() for img in images_text.split(',') if img.strip()]
            
            videos_match = re.search(r'\*\*Videos:\*\*\s*(.+)', assets_text)
            if videos_match:
                videos_text = videos_match.group(1).strip()
                if videos_text:
                    assets['videos'] = [vid.strip() for vid in videos_text.split(',') if vid.strip()]
        
        # Extract main content
        main_content = re.sub(r'^# .+$', '', content, flags=re.MULTILINE)
        main_content = re.sub(r'## Assets.*', '', main_content, flags=re.DOTALL)
        main_content = main_content.strip()
        
        return {
            'title': title,
            'main_content': main_content,
            'assets': assets
        }
    
    def create_claude_prompt(self, extracted_data):
        """Create prompt for Claude Code processing"""
        prompt = f'''Analyze this blog content and generate a JSON blog post structure.

RAW CONTENT:
Title: {extracted_data['title']}

Content:
{extracted_data['main_content']}

Assets: {json.dumps(extracted_data['assets'], indent=2)}

Generate JSON in this exact format:
{{
  "metadata": {{
    "title": "Processed title",
    "slug": "url-friendly-slug-with-hyphens",
    "publishDate": "{datetime.now().strftime('%Y-%m-%d')}",
    "tags": ["relevant", "tags", "here"],
    "excerpt": "Compelling summary under 200 chars",
    "coverImage": "{extracted_data['assets'].get('cover_image', 'cover.jpg')}",
    "featured": false,
    "status": "published"
  }},
  "content": {{
    "subtitle": "Optional subtitle",
    "sections": [
      {{
        "type": "intro",
        "content": {{
          "text": "Opening paragraph"
        }},
        "order": 1
      }},
      {{
        "type": "text",
        "title": "Section Title",
        "content": {{
          "paragraphs": ["Paragraph 1", "Paragraph 2"]
        }},
        "order": 2
      }}
    ]
  }},
  "author": {{
    "name": "Asabaal Horan",
    "signature": "In love and unity,<br><strong>Asabaal Horan</strong><br>Founder, Asabaal Ventures"
  }}
}}

Create 2-4 logical sections, generate relevant tags, make slug lowercase with hyphens. Respond with ONLY the JSON.'''
        
        return prompt
    
    def call_claude_code(self, prompt, filename):
        """Call Claude Code programmatically"""
        print(f"🤖 Calling Claude Code to process: {filename}")
        
        # Create temporary prompt file
        temp_prompt = Path(f"/tmp/claude_prompt_{filename}.txt")
        with open(temp_prompt, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        try:
            # Try different ways to call Claude Code
            methods = [
                # Method 1: Claude with print flag and prompt as argument
                ['claude', '--print', prompt],
                # Method 2: Claude with print flag reading from file
                ['sh', '-c', f'cat {temp_prompt} | claude --print'],
                # Method 3: Claude with specific output format
                ['claude', '--print', '--output-format', 'text', prompt]
            ]
            
            for method in methods:
                try:
                    print(f"Trying method: {' '.join(method)}")
                    result = subprocess.run(
                        method, 
                        capture_output=True, 
                        text=True, 
                        timeout=30,
                        cwd=self.content_dir
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        print("✅ Successfully called Claude Code")
                        return result.stdout.strip()
                    else:
                        print(f"   Return code: {result.returncode}")
                        if result.stderr:
                            print(f"   Error: {result.stderr.strip()}")
                    
                except (subprocess.TimeoutExpired, FileNotFoundError, NotADirectoryError, OSError) as e:
                    print(f"   Failed: {e}")
                    continue
            
            # If all methods fail, provide manual instructions
            print("❌ Could not call Claude Code programmatically")
            print("🔧 Manual process required:")
            print(f"   1. Copy prompt from: {temp_prompt}")
            print("   2. Paste into Claude Code chat")
            print("   3. Save JSON response as: /tmp/claude_response.json")
            print("   4. Run script again with --use-saved-response flag")
            
            return None
            
        finally:
            # Cleanup temp file
            if temp_prompt.exists():
                temp_prompt.unlink()
    
    def save_blog_post(self, json_data, filename):
        """Save the processed blog post"""
        try:
            if isinstance(json_data, str):
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', json_data, re.DOTALL)
                if json_match:
                    json_data = json.loads(json_match.group(0))
                else:
                    json_data = json.loads(json_data)
            
            slug = json_data['metadata']['slug']
            publish_date = json_data['metadata']['publishDate']
            
            # Create output directory
            dir_name = f"{publish_date}_{slug}"
            post_dir = self.output_dir / dir_name
            post_dir.mkdir(parents=True, exist_ok=True)
            
            # Save post.json
            post_file = post_dir / "post.json"
            with open(post_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Blog post saved: {post_file}")
            return post_file
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error processing JSON: {e}")
            print(f"Response was: {json_data}")
            return None
    
    def process_file(self, filename):
        """Process a single blog file"""
        file_path = self.raw_input_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        print(f"🔄 Processing: {filename}")
        
        # Extract content
        extracted_data = self.extract_content_and_assets(file_path)
        print(f"📖 Extracted: {extracted_data['title']}")
        
        # Create prompt
        prompt = self.create_claude_prompt(extracted_data)
        
        # Call Claude Code
        response = self.call_claude_code(prompt, filename.replace('.md', ''))
        
        if response:
            # Save blog post
            return self.save_blog_post(response, filename)
        
        return None

def main():
    """Main execution"""
    print("🤖 Automated Blog Processor")
    print("Programmatically calls Claude Code for processing\n")
    
    processor = AutomatedBlogProcessor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python automated_blog_processor.py filename.md")
        print("  python automated_blog_processor.py --use-saved-response filename.md")
        return
    
    if sys.argv[1] == "--use-saved-response":
        # Use manually saved response
        if len(sys.argv) < 3:
            print("Please provide filename")
            return
        
        filename = sys.argv[2]
        response_file = Path("/tmp/claude_response.json")
        
        if response_file.exists():
            with open(response_file, 'r') as f:
                response = f.read()
            processor.save_blog_post(response, filename)
        else:
            print(f"❌ No saved response found at {response_file}")
    else:
        filename = sys.argv[1]
        result = processor.process_file(filename)
        
        if result:
            print(f"\n🎉 Success! Blog post created: {result}")
        else:
            print(f"\n❌ Failed to process: {filename}")

if __name__ == "__main__":
    main()