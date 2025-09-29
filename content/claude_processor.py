#!/usr/bin/env python3
"""
Claude Processor - Direct integration with this Claude Code conversation
Simply tells you what to ask Claude to do, then handles the response
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

def extract_content_and_assets(file_path):
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

def save_blog_post(json_data, filename):
    """Save the processed blog post"""
    try:
        content_dir = Path(__file__).parent
        output_dir = content_dir / "blog" / "published"
        
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
        post_dir = output_dir / dir_name
        post_dir.mkdir(parents=True, exist_ok=True)
        
        # Save post.json
        post_file = post_dir / "post.json"
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Blog post saved: {post_file}")
        return post_file
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error processing JSON: {e}")
        return None

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("🤖 Claude Processor")
        print("\nUsage:")
        print("  python claude_processor.py filename.md")
        print("\nThis will generate a request for Claude to process in this conversation.")
        return
    
    filename = sys.argv[1]
    content_dir = Path(__file__).parent
    file_path = content_dir / "raw-input" / filename
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Extract content
    extracted_data = extract_content_and_assets(file_path)
    
    print("🤖 AUTOMATED BLOG PROCESSING REQUEST")
    print("=" * 60)
    print(f"📝 Processing: {filename}")
    print(f"📖 Title: {extracted_data['title']}")
    print(f"📊 Assets: {len(extracted_data.get('assets', {}))}")
    print("=" * 60)
    print()
    print("🔥 COPY AND PASTE THIS INTO CLAUDE CODE:")
    print()
    print(f"Please process the file '{filename}' into a blog post JSON structure")
    print()
    print("When Claude responds with the JSON, the script will automatically save it!")

if __name__ == "__main__":
    main()