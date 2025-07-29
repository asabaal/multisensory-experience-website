#!/usr/bin/env python3
"""
Fully Automated Claude Code Blog Processor
Uses OAUTH token to directly call Claude Code for complete automation
"""

import os
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class AutomatedClaudeProcessor:
    def __init__(self):
        """Initialize the automated processor"""
        self.content_dir = Path(__file__).parent
        self.raw_input_dir = self.content_dir / "raw-input"
        self.output_dir = self.content_dir / "blog" / "published"
        
        # Ensure directories exist
        self.raw_input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for OAUTH token
        self.oauth_token = os.getenv('CLAUDE_CODE_OAUTH_TOKEN')
        if not self.oauth_token:
            print("❌ CLAUDE_CODE_OAUTH_TOKEN environment variable not set!")
            print("   Please set it with: export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'")
            sys.exit(1)
    
    def extract_content_and_assets(self, file_path):
        """Extract main content and assets from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first # heading)
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled Post"
        
        # Extract assets section
        assets_match = re.search(r'## Assets\s*\n(.*?)(?:\n---|\n##|\Z)', content, re.DOTALL)
        assets = {}
        
        if assets_match:
            assets_text = assets_match.group(1)
            
            # Extract cover image
            cover_match = re.search(r'\*\*Cover Image:\*\*\s*(.+)', assets_text)
            if cover_match:
                assets['cover_image'] = cover_match.group(1).strip()
            
            # Extract other images
            images_match = re.search(r'\*\*Other Images:\*\*\s*(.+)', assets_text)
            if images_match:
                images_text = images_match.group(1).strip()
                if images_text and images_text != "":
                    images = [img.strip() for img in images_text.split(',') if img.strip()]
                    assets['images'] = images
            
            # Extract videos
            videos_match = re.search(r'\*\*Videos:\*\*\s*(.+)', assets_text)
            if videos_match:
                videos_text = videos_match.group(1).strip()
                if videos_text and videos_text != "":
                    videos = [vid.strip() for vid in videos_text.split(',') if vid.strip()]
                    assets['videos'] = videos
        
        # Extract main content (everything except title and assets)
        main_content = re.sub(r'^# .+$', '', content, flags=re.MULTILINE)  # Remove title
        main_content = re.sub(r'## Assets.*', '', main_content, flags=re.DOTALL)  # Remove assets section
        main_content = main_content.strip()
        
        return {
            'title': title,
            'main_content': main_content,
            'assets': assets
        }
    
    def create_processing_prompt(self, extracted_data):
        """Create the prompt for Claude Code to process the blog content"""
        
        prompt = f"""Please analyze the following raw blog content and generate a structured blog post in JSON format.

## Raw Content:
**Title:** {extracted_data['title']}

**Main Content:**
{extracted_data['main_content']}

**Assets:**
{json.dumps(extracted_data['assets'], indent=2)}

## Task:
Generate a complete JSON blog post structure with:

1. **Metadata** - title, slug, publishDate (today's date), tags (3-5 relevant), excerpt (1-2 sentences), coverImage, featured (false), status (published)
2. **Content Structure** - Break the main content into logical sections:
   - "intro" section with opening paragraph
   - "text" sections with titles for main body paragraphs
   - "quote" sections for any notable quotes you find
   - "image" sections for any images from assets
3. **Author info** - Use standard Asabaal Horan signature

## JSON Format Required:
```json
{{
  "metadata": {{
    "title": "Generated title",
    "slug": "url-friendly-slug-with-hyphens",
    "publishDate": "{datetime.now().strftime('%Y-%m-%d')}",
    "tags": ["tag1", "tag2", "tag3"],
    "excerpt": "Compelling 1-2 sentence summary under 200 chars",
    "coverImage": "{extracted_data['assets'].get('cover_image', 'cover.jpg')}",
    "featured": false,
    "status": "published"
  }},
  "content": {{
    "subtitle": "Optional subtitle if appropriate",
    "sections": [
      {{
        "type": "intro",
        "content": {{
          "text": "Opening paragraph that hooks the reader"
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
```

## Guidelines:
- Create 2-4 main sections based on content length
- Extract meaningful quotes if present in the text
- Generate 3-5 relevant tags that match the content themes
- Make slug lowercase with hyphens (no underscores)
- Keep excerpt compelling and under 200 characters
- Use the cover image from assets if provided
- Structure content with good logical flow
- Break longer paragraphs into readable chunks

Please respond with ONLY the JSON structure, no additional text or formatting."""

        return prompt
    
    def call_claude_code(self, prompt):
        """Call Claude Code programmatically using OAUTH token"""
        try:
            print("🤖 Calling Claude Code API...")
            
            # Use subprocess to call claude CLI with the prompt
            result = subprocess.run([
                'claude',
                '-p', prompt
            ], 
            env={**os.environ, 'CLAUDE_CODE_OAUTH_TOKEN': self.oauth_token},
            capture_output=True, 
            text=True, 
            timeout=120
            )
            
            if result.returncode != 0:
                print(f"❌ Claude Code call failed: {result.stderr}")
                return None
            
            response = result.stdout.strip()
            print("✅ Claude Code response received")
            return response
            
        except subprocess.TimeoutExpired:
            print("❌ Claude Code call timed out")
            return None
        except FileNotFoundError:
            print("❌ Claude CLI not found. Please ensure Claude Code is installed and in PATH")
            return None
        except Exception as e:
            print(f"❌ Error calling Claude Code: {e}")
            return None
    
    def extract_json_from_response(self, response):
        """Extract JSON from Claude's response"""
        try:
            # First try to parse the entire response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from code blocks or find JSON pattern
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'(\{.*?\})'
            ]
            
            for pattern in json_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        continue
            
            print("❌ Could not extract valid JSON from Claude's response")
            print("Raw response:", response[:500] + "..." if len(response) > 500 else response)
            return None
    
    def save_structured_post(self, structured_data, base_filename):
        """Save the structured blog post to the appropriate directory"""
        try:
            slug = structured_data['metadata']['slug']
            publish_date = structured_data['metadata']['publishDate']
            
            # Create directory name with date prefix
            dir_name = f"{publish_date}_{slug}"
            post_dir = self.output_dir / dir_name
            post_dir.mkdir(parents=True, exist_ok=True)
            
            # Save post.json
            post_file = post_dir / "post.json"
            with open(post_file, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Blog post saved: {post_file}")
            return post_file
            
        except KeyError as e:
            print(f"❌ Missing required field in JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Error saving blog post: {e}")
            return None
    
    def process_file(self, filename):
        """Fully automated processing of a raw input file"""
        file_path = self.raw_input_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        print(f"🔄 Processing: {filename}")
        print("=" * 60)
        
        # Step 1: Extract content and assets
        print("📖 Step 1: Extracting content and assets...")
        extracted_data = self.extract_content_and_assets(file_path)
        print(f"   Title: {extracted_data['title']}")
        print(f"   Assets: {len(extracted_data.get('assets', {}))}")
        print(f"   Content length: {len(extracted_data['main_content'])} chars")
        
        # Step 2: Create processing prompt
        print("📝 Step 2: Creating processing prompt...")
        prompt = self.create_processing_prompt(extracted_data)
        
        # Step 3: Call Claude Code
        print("🤖 Step 3: Calling Claude Code for processing...")
        response = self.call_claude_code(prompt)
        
        if not response:
            print("❌ Failed to get response from Claude Code")
            return None
        
        # Step 4: Extract JSON from response
        print("🔍 Step 4: Extracting JSON from response...")
        structured_data = self.extract_json_from_response(response)
        
        if not structured_data:
            print("❌ Failed to extract valid JSON from response")
            return None
        
        # Step 5: Save the structured post
        print("💾 Step 5: Saving structured blog post...")
        base_filename = filename.replace('.md', '')
        post_file = self.save_structured_post(structured_data, base_filename)
        
        if post_file:
            print("=" * 60)
            print("🎉 SUCCESS! Blog post fully automated and saved!")
            print(f"📁 Location: {post_file}")
            print(f"📝 Title: {structured_data['metadata']['title']}")
            print(f"🏷️  Tags: {', '.join(structured_data['metadata']['tags'])}")
            return post_file
        
        return None

def main():
    """Main execution function"""
    print("🚀 Fully Automated Claude Code Blog Processor")
    print("Uses OAUTH token for complete automation - no manual steps!\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python automated_claude_processor.py filename.md")
        print("\nExample:")
        print("  python automated_claude_processor.py test-post.md")
        print("\nMake sure CLAUDE_CODE_OAUTH_TOKEN environment variable is set!")
        return
    
    processor = AutomatedClaudeProcessor()
    filename = sys.argv[1]
    
    result = processor.process_file(filename)
    
    if result:
        print(f"\n✅ Automation complete! Your blog post is ready.")
    else:
        print(f"\n❌ Automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()