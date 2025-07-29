#!/usr/bin/env python3
"""
Claude Code Integrated Blog Processor
Calls Claude Code directly to process blog content with full automation
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

def extract_content_and_assets(file_path):
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

def print_processing_request(extracted_data, filename):
    """Print the request that Claude Code should process"""
    
    request = f"""
🤖 **CLAUDE CODE: Please process this blog content automatically**

**Instructions:** Analyze the content below and respond with a properly formatted JSON blog post structure. Use your full intelligence to create excellent metadata, structure the content logically, and generate compelling excerpts and tags.

---

**Raw Content:**
- **Title:** {extracted_data['title']}
- **Assets:** {json.dumps(extracted_data['assets'], indent=2)}

**Main Content:**
{extracted_data['main_content']}

---

**Required JSON Response Format:**
```json
{{
  "metadata": {{
    "title": "The processed title", 
    "slug": "url-friendly-slug-with-hyphens",
    "publishDate": "{datetime.now().strftime('%Y-%m-%d')}",
    "tags": ["relevant", "tags", "based", "on", "content"],
    "excerpt": "Compelling 1-2 sentence summary under 200 characters that draws readers in",
    "coverImage": "{extracted_data['assets'].get('cover_image', 'cover.jpg')}",
    "featured": false,
    "status": "published"
  }},
  "content": {{
    "subtitle": "Optional compelling subtitle if appropriate",
    "sections": [
      {{
        "type": "intro",
        "content": {{
          "text": "Engaging opening paragraph that hooks the reader"
        }},
        "order": 1
      }},
      {{
        "type": "text",
        "title": "Meaningful Section Title",
        "content": {{
          "paragraphs": ["Well-structured paragraph 1", "Well-structured paragraph 2"]
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

**Guidelines:**
- Create 2-4 logical sections based on content length and natural breaks
- Extract meaningful quotes if they exist in the content
- Generate 3-5 highly relevant tags that match the content themes
- Make slug lowercase with hyphens (no underscores or special chars)
- Keep excerpt compelling and under 200 characters
- Structure content with excellent logical flow
- Break longer content into readable, well-organized sections
- Use the cover image from assets if provided

**Please respond with ONLY the JSON structure - no additional text, formatting, or explanations.**
"""
    
    return request

def save_structured_post(structured_data, base_filename):
    """Save the structured blog post to the appropriate directory"""
    try:
        # Parse JSON if it's a string
        if isinstance(structured_data, str):
            structured_data = json.loads(structured_data)
        
        slug = structured_data['metadata']['slug']
        publish_date = structured_data['metadata']['publishDate']
        
        # Create directory name with date prefix
        dir_name = f"{publish_date}_{slug}"
        output_dir = Path(__file__).parent / "blog" / "published"
        post_dir = output_dir / dir_name
        post_dir.mkdir(parents=True, exist_ok=True)
        
        # Save post.json
        post_file = post_dir / "post.json"
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Blog post saved: {post_file}")
        return post_file
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error saving blog post: {e}")
        return None

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python process_with_claude.py filename.md")
        print("       python process_with_claude.py --save-response 'json_response_here' filename")
        return
    
    if sys.argv[1] == "--save-response":
        # Save Claude's JSON response
        if len(sys.argv) < 4:
            print("Usage: python process_with_claude.py --save-response 'json_response' filename")
            return
        
        json_response = sys.argv[2]
        base_filename = sys.argv[3].replace('.md', '')
        
        result = save_structured_post(json_response, base_filename)
        if result:
            print(f"🎉 Successfully created blog post!")
        return
    
    # Process file and generate request for Claude
    filename = sys.argv[1]
    file_path = Path(__file__).parent / "raw-input" / filename
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"🔄 Processing: {filename}")
    
    # Extract content
    extracted_data = extract_content_and_assets(file_path)
    
    # Print the request for Claude Code
    request = print_processing_request(extracted_data, filename)
    
    print("=" * 80)
    print("📋 COPY THE FOLLOWING REQUEST AND PASTE IT INTO CLAUDE CODE:")
    print("=" * 80)
    print(request)
    print("=" * 80)
    print()
    print("After Claude responds with JSON, run:")
    print(f"python process_with_claude.py --save-response 'PASTE_CLAUDE_JSON_HERE' {filename}")

if __name__ == "__main__":
    main()