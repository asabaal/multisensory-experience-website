#!/usr/bin/env python3
"""
Simple Blog Processor - Streamlined workflow with Claude Code
Creates perfect prompts and handles responses automatically
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

class SimpleBlogProcessor:
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
    
    def generate_prompt(self, filename):
        """Generate a prompt for Claude to process"""
        file_path = self.raw_input_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        extracted_data = self.extract_content_and_assets(file_path)
        
        prompt = f"""Process this blog content into a structured JSON blog post:

**Title:** {extracted_data['title']}

**Content:**
{extracted_data['main_content']}

**Assets:** {json.dumps(extracted_data['assets'], indent=2)}

**Required JSON format:**
```json
{{
  "metadata": {{
    "title": "{extracted_data['title']}",
    "slug": "create-url-friendly-slug-here",
    "publishDate": "{datetime.now().strftime('%Y-%m-%d')}",
    "tags": ["create", "relevant", "tags"],
    "excerpt": "Write compelling summary under 200 characters",
    "coverImage": "{extracted_data['assets'].get('cover_image', 'cover.jpg')}",
    "featured": false,
    "status": "published"
  }},
  "content": {{
    "subtitle": "Optional compelling subtitle",
    "sections": [
      {{
        "type": "intro",
        "content": {{
          "text": "Write engaging opening paragraph"
        }},
        "order": 1
      }},
      {{
        "type": "text",
        "title": "Create Section Title",
        "content": {{
          "paragraphs": ["Write paragraph 1", "Write paragraph 2"]
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
```

**Instructions:**
- Create 2-4 logical sections from the content
- Generate 3-5 relevant tags
- Make slug lowercase with hyphens
- Keep excerpt under 200 characters
- Break content into well-structured sections
- Add image sections for assets if needed

**Respond with ONLY the JSON - no additional text.**"""

        return prompt, extracted_data
    
    def save_response(self, json_response, filename):
        """Save Claude's JSON response as a blog post"""
        try:
            # Parse JSON if it's a string
            if isinstance(json_response, str):
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', json_response, re.DOTALL)
                if json_match:
                    json_data = json.loads(json_match.group(0))
                else:
                    json_data = json.loads(json_response)
            else:
                json_data = json_response
            
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
            print("Make sure Claude's response contains valid JSON")
            return None

def main():
    """Main execution"""
    processor = SimpleBlogProcessor()
    
    if len(sys.argv) < 2:
        print("🤖 Simple Blog Processor")
        print("\nUsage:")
        print("  Step 1: python simple_blog_processor.py filename.md")
        print("  Step 2: Copy the prompt and paste it into Claude Code")
        print("  Step 3: python simple_blog_processor.py --save filename.md 'CLAUDE_JSON_RESPONSE'")
        print("\nExample:")
        print("  python simple_blog_processor.py test-post.md")
        return
    
    if sys.argv[1] == "--save":
        if len(sys.argv) < 4:
            print("Usage: python simple_blog_processor.py --save filename.md 'json_response'")
            return
        
        filename = sys.argv[2]
        json_response = sys.argv[3]
        
        result = processor.save_response(json_response, filename)
        if result:
            print("🎉 Blog post successfully created!")
        return
    
    # Generate prompt
    filename = sys.argv[1]
    prompt_result = processor.generate_prompt(filename)
    
    if prompt_result:
        prompt, extracted_data = prompt_result
        print("📋 COPY THE FOLLOWING PROMPT AND PASTE INTO CLAUDE CODE:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        print("\nAfter Claude responds, run:")
        print(f"python simple_blog_processor.py --save {filename} 'PASTE_CLAUDE_JSON_RESPONSE_HERE'")

if __name__ == "__main__":
    main()