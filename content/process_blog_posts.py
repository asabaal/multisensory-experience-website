#!/usr/bin/env python3
"""
Agentic Blog Post Processor
Uses Claude API to intelligently convert simple raw content into structured blog posts
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
import anthropic

class BlogPostProcessor:
    def __init__(self, api_key=None):
        """Initialize with Claude API key"""
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("Please set ANTHROPIC_API_KEY environment variable or pass api_key")
        
        self.client = anthropic.Anthropic(api_key=api_key)
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
                images = [img.strip() for img in images_match.group(1).split(',')]
                assets['images'] = images
            
            # Extract videos
            videos_match = re.search(r'\*\*Videos:\*\*\s*(.+)', assets_text)
            if videos_match:
                videos = [vid.strip() for vid in videos_match.group(1).split(',')]
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
    
    def generate_blog_structure(self, extracted_data):
        """Use Claude API to generate structured blog post metadata and content"""
        
        prompt = f"""
        You are an expert blog post structurer. Given the raw content below, create a structured blog post with:
        
        1. Generate appropriate metadata (slug, tags, excerpt, publish date)
        2. Structure the content into logical sections
        3. Extract any notable quotes for highlighting
        4. Create a compelling excerpt
        
        Raw Content:
        Title: {extracted_data['title']}
        Content: {extracted_data['main_content']}
        
        Please respond with a JSON structure matching this format:
        {{
            "metadata": {{
                "title": "Generated title",
                "slug": "url-friendly-slug",
                "publishDate": "2025-01-29",
                "tags": ["tag1", "tag2", "tag3"],
                "excerpt": "Compelling 1-2 sentence summary",
                "coverImage": "cover.jpg",
                "featured": false,
                "status": "published"
            }},
            "content": {{
                "subtitle": "Optional subtitle",
                "sections": [
                    {{
                        "type": "intro",
                        "content": {{
                            "text": "Introductory paragraph"
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
                    }},
                    {{
                        "type": "quote",
                        "content": {{
                            "text": "Notable quote from content",
                            "author": "Asabaal Horan"
                        }},
                        "order": 3
                    }}
                ]
            }},
            "author": {{
                "name": "Asabaal Horan",
                "signature": "In love and unity,<br><strong>Asabaal Horan</strong><br>Founder, Asabaal Ventures"
            }}
        }}
        
        Guidelines:
        - Create 2-4 sections based on content length
        - Extract 1-2 meaningful quotes if present
        - Generate 3-5 relevant tags
        - Make slug URL-friendly (lowercase, hyphens)
        - Keep excerpt under 200 characters
        - Structure content logically with good flow
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the JSON response
        try:
            structured_data = json.loads(response.content[0].text)
            
            # Add cover image from assets if available
            if 'cover_image' in extracted_data['assets']:
                structured_data['metadata']['coverImage'] = extracted_data['assets']['cover_image']
            
            # Add other assets if present
            if 'images' in extracted_data['assets'] or 'videos' in extracted_data['assets']:
                # Add image and video sections
                order = len(structured_data['content']['sections']) + 1
                
                if 'images' in extracted_data['assets']:
                    for img in extracted_data['assets']['images']:
                        structured_data['content']['sections'].append({
                            "type": "image",
                            "content": {
                                "src": f"assets/{img}",
                                "alt": f"Image from {structured_data['metadata']['title']}",
                                "caption": ""
                            },
                            "order": order
                        })
                        order += 1
                
                # Note: Videos would need special handling based on your blog system
                
            return structured_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Claude response: {e}")
            print(f"Response was: {response.content[0].text}")
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
        
        print(f"✅ Generated: {post_file}")
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
        
        # Generate structured blog post using Claude API
        structured_data = self.generate_blog_structure(extracted_data)
        
        if not structured_data:
            print(f"❌ Failed to generate structure for: {filename}")
            return None
        
        # Save the structured post
        return self.save_structured_post(structured_data, filename)
    
    def process_all_files(self):
        """Process all .md files in raw-input directory"""
        raw_files = list(self.raw_input_dir.glob("*.md"))
        
        # Skip template files
        raw_files = [f for f in raw_files if f.name not in ['TEMPLATE.md', 'SIMPLE-TEMPLATE.md', 'README.md']]
        
        print(f"🚀 Found {len(raw_files)} files to process")
        
        results = []
        for file_path in raw_files:
            result = self.process_file(file_path.name)
            if result:
                results.append(result)
        
        print(f"\n✅ Successfully processed {len(results)} blog posts!")
        return results

def main():
    """Main execution function"""
    print("🤖 Agentic Blog Post Processor")
    print("Uses Claude API to intelligently structure your raw content\n")
    
    try:
        processor = BlogPostProcessor()
        
        # Check if user wants to process a specific file or all files
        import sys
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            processor.process_file(filename)
        else:
            processor.process_all_files()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Set ANTHROPIC_API_KEY environment variable")
        print("2. Install required packages: pip install anthropic")

if __name__ == "__main__":
    main()