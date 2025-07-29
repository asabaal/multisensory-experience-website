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
            
            print(f"✅ Blog post JSON saved: {post_file}")
            return post_file
            
        except KeyError as e:
            print(f"❌ Missing required field in JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Error saving blog post: {e}")
            return None
    
    def generate_html_from_json(self, structured_data):
        """Generate beautiful HTML blog post from JSON structure"""
        try:
            metadata = structured_data['metadata'] 
            content = structured_data['content']
            author = structured_data['author']
            
            # Generate tags HTML
            tags_html = '\n'.join([f'                        <span class="tag">{tag}</span>' 
                                  for tag in metadata['tags']])
            
            # Generate content sections HTML
            sections_html = ""
            for section in content['sections']:
                if section['type'] == 'intro':
                    sections_html += f"""
                <div class="intro-section">
                    <div class="intro-text">
                        {section['content']['text']}
                    </div>
                </div>
"""
                elif section['type'] == 'text':
                    title = section.get('title', '')
                    title_html = f'<h2 class="section-title">{title}</h2>' if title else ''
                    
                    paragraphs = section['content']['paragraphs']
                    paragraphs_html = '\n'.join([f'                        <p>{para}</p>' 
                                               for para in paragraphs])
                    
                    sections_html += f"""
                <div class="content-section">
                    {title_html}
                    <div class="content-text">
{paragraphs_html}
                    </div>
                </div>
"""
                elif section['type'] == 'quote':
                    quote_text = section['content']['text']
                    sections_html += f"""
                <div class="quote-section">
                    <div class="quote-text">
                        "{quote_text}"
                    </div>
                </div>
"""
                elif section['type'] == 'image':
                    image_url = section['content']['url']
                    alt_text = section['content'].get('alt', metadata['title'])
                    sections_html += f"""
                <div class="image-section">
                    <div class="content-image">
                        <img src="{image_url}" alt="{alt_text}" class="section-img">
                    </div>
                </div>
"""
            
            # Generate HTML template
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} | Asabaal Ventures Blog</title>
    <meta name="description" content="{metadata['excerpt']}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 25%, #2d1b69 50%, #4c1d95 75%, #6b21a8 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
            padding-top: 70px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header Styles */
        .header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(15, 15, 35, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .nav {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
        }}
        
        .nav-links {{
            display: flex;
            gap: 30px;
            list-style: none;
            margin: 0;
            padding: 0;
        }}
        
        .nav-links a {{
            color: #e5e7eb;
            text-decoration: none;
            transition: color 0.3s ease;
            font-weight: 500;
        }}
        
        .nav-links a:hover {{
            color: #fbbf24;
        }}

        /* Post Header */
        .post-header {{
            padding: 100px 0 60px;
            text-align: center;
            position: relative;
            background: radial-gradient(circle at 50% 50%, rgba(251, 191, 36, 0.15) 0%, transparent 70%);
        }}

        .back-link {{
            position: absolute;
            top: 120px;
            left: 20px;
            color: #06b6d4;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }}

        .back-link:hover {{
            color: #fbbf24;
        }}

        .post-title {{
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 25px;
            background: linear-gradient(45deg, #fbbf24, #f472b6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}

        .post-meta {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}

        .post-date {{
            background: linear-gradient(45deg, #8b5cf6, #ec4899);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 0.9rem;
        }}

        .post-tags {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .tag {{
            background: rgba(255, 255, 255, 0.1);
            color: #d1d5db;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .post-subtitle {{
            font-size: 1.3rem;
            color: #d1d5db;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
        }}

        /* Featured Image */
        .featured-image {{
            padding: 60px 0;
            background: rgba(0, 0, 0, 0.2);
        }}

        .image-container {{
            max-width: 800px;
            margin: 0 auto;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}

        .featured-img {{
            width: 100%;
            height: 400px;
            object-fit: cover;
        }}

        /* Post Content */
        .post-content {{
            padding: 80px 0;
            background: rgba(0, 0, 0, 0.3);
        }}

        .content-wrapper {{
            max-width: 800px;
            margin: 0 auto;
        }}

        .intro-section {{
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #fbbf24;
            padding: 30px;
            margin-bottom: 60px;
            border-radius: 10px;
            font-style: italic;
        }}

        .intro-text {{
            font-size: 1.3rem;
            color: #e5e7eb;
            line-height: 1.7;
        }}

        .content-section {{
            margin-bottom: 60px;
        }}

        .section-title {{
            font-size: 2rem;
            color: #fbbf24;
            margin-bottom: 25px;
            font-weight: 700;
        }}

        .content-text {{
            font-size: 1.2rem;
            line-height: 1.8;
            color: #e5e7eb;
            margin-bottom: 30px;
        }}

        .content-text p {{
            margin-bottom: 20px;
        }}

        .quote-section {{
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #fbbf24;
            padding: 30px;
            margin: 40px 0;
            border-radius: 10px;
            font-style: italic;
        }}

        .quote-text {{
            font-size: 1.4rem;
            color: #d1d5db;
            margin-bottom: 15px;
        }}

        .image-section {{
            margin: 40px 0;
        }}

        .content-image {{
            text-align: center;
        }}

        .section-img {{
            max-width: 100%;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 15px 35px -10px rgba(139, 92, 246, 0.3);
        }}

        /* Author Section */
        .author-section {{
            padding: 60px 0;
            background: rgba(0, 0, 0, 0.4);
            text-align: center;
        }}

        .author-signature {{
            font-size: 1.1rem;
            color: #d1d5db;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }}

        /* Navigation */
        .post-navigation {{
            padding: 60px 0;
            background: rgba(0, 0, 0, 0.4);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .nav-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .nav-button {{
            background: linear-gradient(45deg, #8b5cf6, #06b6d4);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 50px;
            font-weight: bold;
            text-decoration: none;
            transition: transform 0.3s ease;
        }}

        .nav-button:hover {{
            transform: scale(1.05);
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .post-title {{ font-size: 2.5rem; }}
            .back-link {{ position: static; margin-bottom: 20px; display: inline-block; }}
            .post-meta {{ flex-direction: column; gap: 15px; }}
            .nav-content {{ flex-direction: column; text-align: center; }}
            .nav-links {{ gap: 15px; font-size: 0.9rem; }}
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <nav class="nav">
                <ul class="nav-links">
                    <li><a href="../index.html">Home</a></li>
                    <li><a href="../vision_2054_page.html">Vision 2054</a></li>
                    <li><a href="../index.html#videos">Videos</a></li>
                    <li><a href="../unity-remix-contest.html">Contest</a></li>
                    <li><a href="../blog.html">Blog</a></li>
                    <li><a href="#contact">Connect</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- Post Header -->
    <section class="post-header">
        <div class="container">
            <a href="../blog.html" class="back-link">← Back to Blog</a>
            <h1 class="post-title">{metadata['title']}</h1>
            <div class="post-meta">
                <span class="post-date">{metadata['publishDate']}</span>
                <div class="post-tags">
{tags_html}
                </div>
            </div>
            <p class="post-subtitle">
                {metadata['excerpt']}
            </p>
        </div>
    </section>

    <!-- Featured Image -->
    <section class="featured-image">
        <div class="container">
            <div class="image-container">
                <img src="../assets/images/blog/{metadata['coverImage']}" alt="{metadata['title']}" class="featured-img">
            </div>
        </div>
    </section>

    <!-- Post Content -->
    <section class="post-content">
        <div class="container">
            <div class="content-wrapper">
{sections_html}
            </div>
        </div>
    </section>

    <!-- Author Section -->
    <section class="author-section">
        <div class="container">
            <div class="author-signature">
                {author['signature']}
            </div>
        </div>
    </section>

    <!-- Post Navigation -->
    <section class="post-navigation">
        <div class="container">
            <div class="nav-content">
                <div class="prev-post">
                    <!-- Previous post link will be added dynamically -->
                </div>
                <a href="../blog.html" class="nav-button">All Posts</a>
                <div class="next-post">
                    <!-- Next post link will be added dynamically -->
                </div>
            </div>
        </div>
    </section>
</body>
</html>"""
            
            return html_content
            
        except KeyError as e:
            print(f"❌ Missing required field for HTML generation: {e}")
            return None
        except Exception as e:
            print(f"❌ Error generating HTML: {e}")
            return None
    
    def save_html_blog_post(self, structured_data, base_filename):
        """Generate and save the HTML blog post"""
        try:
            # Generate HTML content
            html_content = self.generate_html_from_json(structured_data)
            if not html_content:
                return None
            
            slug = structured_data['metadata']['slug']
            
            # Save HTML file directly in blog directory
            blog_dir = self.content_dir.parent / "blog"
            blog_dir.mkdir(exist_ok=True)
            
            html_file = blog_dir / f"post-{slug}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML blog post saved: {html_file}")
            return html_file
            
        except Exception as e:
            print(f"❌ Error saving HTML blog post: {e}")
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
        
        # Step 5: Save the structured post (JSON)
        print("💾 Step 5: Saving structured blog post JSON...")
        base_filename = filename.replace('.md', '')
        post_file = self.save_structured_post(structured_data, base_filename)
        
        if not post_file:
            print("❌ Failed to save JSON structure")
            return None
        
        # Step 6: Generate and save HTML blog post
        print("🎨 Step 6: Generating beautiful HTML blog post...")
        html_file = self.save_html_blog_post(structured_data, base_filename)
        
        if html_file:
            print("=" * 60)
            print("🎉 SUCCESS! Complete blog automation pipeline finished!")
            print(f"📁 JSON Location: {post_file}")
            print(f"🌐 HTML Location: {html_file}")
            print(f"📝 Title: {structured_data['metadata']['title']}")
            print(f"🏷️  Tags: {', '.join(structured_data['metadata']['tags'])}")
            print(f"🔗 Blog URL: blog/post-{structured_data['metadata']['slug']}.html")
            return {'json': post_file, 'html': html_file}
        else:
            print("⚠️  JSON saved but HTML generation failed")
            return {'json': post_file, 'html': None}
        
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