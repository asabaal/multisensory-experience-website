#!/usr/bin/env python3
"""
Claude Code Native Blog Post Processor
Uses Claude Code's built-in intelligence to convert simple raw content into structured blog posts
No external API calls needed - fully integrated with Claude Code!
"""

import os
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class ClaudeBlogProcessor:
    def __init__(self):
        """Initialize the Claude Code native processor"""
        self.raw_input_dir = Path(__file__).parent / "raw-input"
        self.output_dir = Path(__file__).parent / "blog" / "published"
        self.claude_prompts_dir = Path(__file__).parent / "claude-prompts"
        
        # Create prompts directory if it doesn't exist
        self.claude_prompts_dir.mkdir(exist_ok=True)
        
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
    
    def create_claude_prompt(self, extracted_data):
        """Create a detailed prompt for Claude Code to process"""
        
        prompt_content = f"""# Blog Post Processing Request

Please analyze the following raw blog content and generate a structured blog post in JSON format.

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
    "coverImage": "cover.jpg",
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

Please respond with ONLY the JSON structure, no additional text or formatting.
"""
        
        return prompt_content
    
    def save_prompt_and_get_response(self, prompt_content, filename):
        """Save prompt to file and instruct user how to get Claude's response"""
        
        # Create prompt file
        prompt_file = self.claude_prompts_dir / f"{filename}_prompt.md"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
        # Create response file placeholder
        response_file = self.claude_prompts_dir / f"{filename}_response.json"
        
        print(f"📝 Prompt saved to: {prompt_file}")
        print(f"🤖 Now:")
        print(f"   1. Copy the content from: {prompt_file}")
        print(f"   2. Paste it into Claude Code (this conversation)")
        print(f"   3. Copy Claude's JSON response")
        print(f"   4. Save it as: {response_file}")
        print(f"   5. Run: python claude_blog_processor.py --process-response {filename}")
        
        return prompt_file, response_file
    
    def process_claude_response(self, filename):
        """Process Claude's JSON response and create the final blog post"""
        
        response_file = self.claude_prompts_dir / f"{filename}_response.json"
        
        if not response_file.exists():
            print(f"❌ Response file not found: {response_file}")
            print("Please save Claude's JSON response to this file first.")
            return None
        
        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                structured_data = json.load(f)
            
            # Save the structured post
            return self.save_structured_post(structured_data, filename)
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            print(f"Please check the format in: {response_file}")
            return None
        except Exception as e:
            print(f"❌ Error processing response: {e}")
            return None
    
    def save_structured_post(self, structured_data, filename):
        """Save the structured blog post to the appropriate directory"""
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
    
    def process_file(self, filename):
        """Process a single raw input file"""
        file_path = self.raw_input_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        print(f"🔄 Processing: {filename}")
        
        # Extract content and assets
        extracted_data = self.extract_content_and_assets(file_path)
        
        # Create Claude prompt
        prompt_content = self.create_claude_prompt(extracted_data)
        
        # Save prompt and provide instructions
        base_filename = filename.replace('.md', '')
        prompt_file, response_file = self.save_prompt_and_get_response(prompt_content, base_filename)
        
        return prompt_file

def main():
    """Main execution function"""
    print("🤖 Claude Code Native Blog Post Processor")
    print("Uses Claude Code's built-in intelligence - no external APIs!\n")
    
    processor = ClaudeBlogProcessor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Generate prompt:     python claude_blog_processor.py filename.md")
        print("  Process response:    python claude_blog_processor.py --process-response filename")
        print("  Example:            python claude_blog_processor.py test-post.md")
        return
    
    if sys.argv[1] == "--process-response":
        if len(sys.argv) < 3:
            print("❌ Please provide filename for response processing")
            return
        filename = sys.argv[2]
        processor.process_claude_response(filename)
    else:
        filename = sys.argv[1]
        processor.process_file(filename)

if __name__ == "__main__":
    main()