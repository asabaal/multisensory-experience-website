#!/usr/bin/env python3
"""
Fully Automated Claude Code Blog Processor
Uses Claude Code's Task tool for complete automation - no manual steps!
"""

import os
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class AutoBlogProcessor:
    def __init__(self):
        """Initialize the fully automated processor"""
        self.raw_input_dir = Path(__file__).parent / "raw-input"
        self.output_dir = Path(__file__).parent / "blog" / "published"
        
    def extract_content_and_assets(self, file_path):
        """Extract main content and assets from simple markdown file"""
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
    
    def create_processing_request(self, extracted_data):
        """Create a processing request that Claude Code can handle automatically"""
        
        request = f"""AUTOMATED BLOG POST PROCESSING REQUEST

Please process this raw blog content and respond with ONLY a valid JSON structure (no additional text or markdown formatting).

RAW CONTENT:
Title: {extracted_data['title']}

Content:
{extracted_data['main_content']}

Assets: {json.dumps(extracted_data['assets'], indent=2)}

REQUIRED JSON FORMAT:
{{
  "metadata": {{
    "title": "The processed title",
    "slug": "url-friendly-slug-with-hyphens",
    "publishDate": "{datetime.now().strftime('%Y-%m-%d')}",
    "tags": ["relevant", "tags", "here"],
    "excerpt": "Compelling 1-2 sentence summary under 200 characters",
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
          "paragraphs": ["Content paragraph 1", "Content paragraph 2"]
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

INSTRUCTIONS:
- Create 2-4 logical sections based on content
- Extract quotes if meaningful ones exist
- Generate 3-5 relevant tags
- Make slug lowercase with hyphens
- Keep excerpt under 200 chars
- Structure content with good flow
- Use provided cover image from assets
- Respond with ONLY the JSON, no other text"""
        
        return request
    
    def call_claude_code_task(self, request, filename):
        """Use Claude Code to process the content automatically"""
        
        print(f"🤖 Calling Claude Code to process: {filename}")
        print("🔄 Processing with full Claude intelligence...")
        
        # Create a temporary file with the request
        temp_request_file = Path(f"/tmp/blog_request_{filename}.txt")
        with open(temp_request_file, 'w', encoding='utf-8') as f:
            f.write(request)
        
        try:
            # Use claude command to process the request
            # This simulates what would happen with the Task tool
            result = subprocess.run([
                'claude', 'code', '--prompt-file', str(temp_request_file)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json_match.group(0)
                else:
                    return response
            else:
                print(f"❌ Error calling Claude Code: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Claude Code call timed out")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        finally:
            # Clean up temp file
            if temp_request_file.exists():
                temp_request_file.unlink()
    
    def save_structured_post(self, structured_data, filename):
        """Save the structured blog post to the appropriate directory"""
        try:
            # Parse JSON if it's a string
            if isinstance(structured_data, str):
                structured_data = json.loads(structured_data)
            
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
            
            print(f"✅ Generated blog post: {post_file}")
            return post_file
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing Claude response as JSON: {e}")
            print(f"Response was: {structured_data}")
            return None
        except Exception as e:
            print(f"❌ Error saving blog post: {e}")
            return None
    
    def process_file(self, filename):
        """Process a single raw input file completely automatically"""
        file_path = self.raw_input_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        print(f"🚀 Auto-processing: {filename}")
        
        # Extract content and assets
        extracted_data = self.extract_content_and_assets(file_path)
        print(f"📖 Extracted: {extracted_data['title']}")
        
        # Create processing request
        request = self.create_processing_request(extracted_data)
        
        # Call Claude Code to process
        claude_response = self.call_claude_code_task(request, filename.replace('.md', ''))
        
        if not claude_response:
            print(f"❌ Failed to get response from Claude Code for: {filename}")
            return None
        
        # Save the structured post
        return self.save_structured_post(claude_response, filename)

def main():
    """Main execution function"""
    print("🤖 Fully Automated Claude Code Blog Processor")
    print("Complete automation - no manual steps required!\n")
    
    processor = AutoBlogProcessor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Process file:       python auto_blog_processor.py filename.md")
        print("  Example:           python auto_blog_processor.py test-post.md")
        return
    
    filename = sys.argv[1]
    result = processor.process_file(filename)
    
    if result:
        print(f"\n🎉 Success! Blog post automatically generated at: {result}")
    else:
        print(f"\n❌ Failed to process: {filename}")

if __name__ == "__main__":
    main()