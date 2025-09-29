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
import time
from datetime import datetime
from pathlib import Path

class AutomatedClaudeProcessor:
    def __init__(self, verbose=True, auto_update=False):
        """Initialize the automated processor
        
        Args:
            verbose: Show detailed timing information
            auto_update: Automatically update existing posts without prompting
        """
        self.verbose = verbose
        self.auto_update = auto_update
        self.max_iterations = 3  # Maximum iterations for Claude to get it right
        self.start_time = time.time()
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
        else:
            print(f"🔑 OAUTH token found: {self.oauth_token[:20]}..." if len(self.oauth_token) > 20 else "🔑 OAUTH token found (short)")
    
    def log_time(self, message, start_time=None):
        """Log a message with timestamp and duration"""
        if not self.verbose:
            return
        current_time = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')
        if start_time:
            duration = current_time - start_time
            print(f"[{timestamp}] {message} (took {duration:.1f}s)")
        else:
            print(f"[{timestamp}] {message}")
        return current_time
    
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
        publish_date = None
        
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
            
            # Extract videos using line-by-line approach to avoid regex issues
            videos_text = ""
            for line in assets_text.split('\n'):
                if line.strip().startswith('**Videos:**'):
                    videos_text = line.replace('**Videos:**', '').strip()
                    break
            
            if self.verbose:
                print(f"   🎬 Raw videos text: '{videos_text}'")
            
            if videos_text and videos_text != "":
                videos = [vid.strip() for vid in videos_text.split(',') if vid.strip()]
                if self.verbose:
                    print(f"   🎬 Parsed videos: {videos}")
                assets['videos'] = videos
            else:
                if self.verbose:
                    print(f"   🎬 No videos found - will show placeholder")
            
            # Extract publish date
            publish_date_match = re.search(r'\*\*Publish Date\*?\*?:?\s*(.+)', assets_text)
            if publish_date_match:
                date_str = publish_date_match.group(1).strip()
                print(f"📅 Found publish date in raw input: '{date_str}'")
                # Handle different date formats: YYYYMMDD, YYYY-MM-DD, etc.
                if len(date_str) == 8 and date_str.isdigit():  # YYYYMMDD format
                    publish_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    print(f"📅 Converted to: {publish_date}")
                elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):  # YYYY-MM-DD format
                    publish_date = date_str
                    print(f"📅 Using as-is: {publish_date}")
                else:
                    print(f"⚠️  Unrecognized date format: {date_str}, using today's date")
                    publish_date = datetime.now().strftime('%Y-%m-%d')
            else:
                print("⚠️  No publish date found in assets section")
        
        # Extract main content (everything except title and assets)
        main_content = re.sub(r'^# .+$', '', content, flags=re.MULTILINE)  # Remove title
        main_content = re.sub(r'## Assets.*', '', main_content, flags=re.DOTALL)  # Remove assets section
        main_content = main_content.strip()
        
        return {
            'title': title,
            'main_content': main_content,
            'assets': assets,
            'publish_date': publish_date or datetime.now().strftime('%Y-%m-%d')
        }
    
    def create_processing_prompt(self, extracted_data):
        """Create the prompt for Claude Code to process the blog content"""
        
        # Format the video handling instructions
        video_instructions = ""
        if 'videos' in extracted_data['assets'] and extracted_data['assets']['videos']:
            video_count = len(extracted_data['assets']['videos'])
            if video_count == 1:
                video_instructions = "IMPORTANT: Create a featured video section as the FIRST section (order: 0) using the provided video."
            else:
                video_instructions = f"""IMPORTANT: You have {video_count} videos to place strategically:
- Use the FIRST video as a featured video section (order: 0) at the top
- Place additional videos as inline video sections throughout the content where contextually appropriate
- Consider video titles/context if available to determine best placement"""

        # Format image handling instructions
        image_instructions = ""
        if 'images' in extracted_data['assets'] and extracted_data['assets']['images']:
            images = extracted_data['assets']['images']
            if 'in-love-and-unity.jpg' in images or 'in-love-and-unity.png' in images:
                image_instructions = "CRITICAL: You MUST include the 'in-love-and-unity' image as the FINAL section before the conclusion. This is Asabaal's signature image that appears in every post as a sign-off."
            else:
                image_instructions = f"IMPORTANT: Include the provided images contextually within the content: {', '.join(images)}"
        
        prompt = f"""Please analyze the following raw blog content and generate a structured blog post in JSON format.

## Raw Content:
**Title:** {extracted_data['title']}
**Publish Date:** {extracted_data['publish_date']} (USE THIS EXACT DATE - DO NOT USE TODAY'S DATE)

**Main Content:**
{extracted_data['main_content']}

**Assets:**
{json.dumps(extracted_data['assets'], indent=2)}

## Task:
{video_instructions}
{image_instructions}

Generate a complete JSON blog post structure with:

1. **Metadata** - title, slug, publishDate (USE THE PROVIDED DATE: {extracted_data['publish_date']}), tags (3-5 relevant), excerpt (1-2 sentences), coverImage, featured (false), status (published)
2. **Content Structure** - Break the main content into logical sections:
   - "intro" section with opening paragraph
   - "text" sections with titles for main body paragraphs
   - "quote" sections for any notable quotes you find
   - "video" sections for videos from assets (see video instructions above)
   - "image" sections for any images from assets
3. **Author info** - Use standard Asabaal Horan signature

## JSON Format Required:
```json
{{
  "metadata": {{
    "title": "Generated title",
    "slug": "url-friendly-slug-with-hyphens",
    "publishDate": "{extracted_data['publish_date']}",
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
        "type": "video",
        "content": {{
          "url": "https://youtube.com/watch?v=video-id",
          "title": "Video Title (optional)"
        }},
        "order": 0
      }},
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
      }},
      {{
        "type": "video",
        "content": {{
          "url": "https://youtube.com/watch?v=second-video",
          "title": "Additional Video Title"
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
```

## Guidelines:
- **CRITICAL: Use the exact publish date provided: {extracted_data['publish_date']} - DO NOT use today's date**
- Create 2-4 main sections based on content length
- Extract meaningful quotes if present in the text
- Generate 3-5 relevant tags that match the content themes
- Make slug lowercase with hyphens (no underscores)
- Keep excerpt compelling and under 200 characters
- Use the cover image from assets if provided
- Structure content with good logical flow
- **Video Handling:**
  - If 1 video: Place as featured video (order: 0)
  - If multiple videos: First video featured (order: 0), others placed contextually throughout content
  - Always include video title if you can infer it from context or URL
- Break longer paragraphs into readable chunks

Please respond with ONLY the JSON structure, no additional text or formatting."""

        return prompt
    
    def call_claude_code(self, prompt):
        """Call Claude Code programmatically using OAUTH token"""
        try:
            api_start = time.time()
            print("🤖 Calling Claude Code API...")
            print(f"📝 Prompt length: {len(prompt)} characters")
            
            # Use subprocess to call claude CLI with the prompt
            cmd = ['claude', '-p', prompt]
            print(f"🚀 Executing command: {' '.join(cmd[:2])} [prompt...]")
            self.log_time("Claude API call started")
            
            result = subprocess.run(cmd, 
            env={**os.environ, 'CLAUDE_CODE_OAUTH_TOKEN': self.oauth_token},
            capture_output=True, 
            text=True, 
            timeout=120
            )
            
            if result.returncode != 0:
                print(f"❌ Claude Code call failed (return code: {result.returncode})")
                print(f"Error output: {result.stderr}")
                return None
            
            response = result.stdout.strip()
            api_duration = time.time() - api_start
            print("✅ Claude Code response received")
            self.log_time(f"Claude API call completed", api_start)
            print(f"🔍 Response length: {len(response)} characters")
            
            if not response:
                print("⚠️  Response is empty after stripping whitespace")
                print(f"Raw stdout: '{result.stdout}'")
                print(f"Raw stderr: '{result.stderr}'")
                return None
                
            return response
            
        except subprocess.TimeoutExpired:
            api_duration = time.time() - api_start
            print(f"❌ Claude Code call timed out after {api_duration:.1f} seconds")
            return None
        except FileNotFoundError:
            print("❌ Claude CLI not found. Please ensure Claude Code is installed and in PATH")
            return None
        except Exception as e:
            print(f"❌ Error calling Claude Code: {e}")
            return None
    
    def validate_claude_response(self, structured_data, extracted_data):
        """
        Validate that Claude followed all instructions correctly
        Returns: (is_valid: bool, issues: list[str])
        """
        issues = []
        
        # Check if in-love-and-unity image should be included
        if 'images' in extracted_data['assets'] and extracted_data['assets']['images']:
            images = extracted_data['assets']['images']
            if self.verbose:
                print(f"   🖼️  Other images found: {images}")
            if 'in-love-and-unity.jpg' in images or 'in-love-and-unity.png' in images:
                # Check if in-love-and-unity image is included in sections
                has_unity_image = any(
                    section.get('type') == 'image' and 
                    section.get('content', {}).get('src', '').find('in-love-and-unity') != -1
                    for section in structured_data.get('content', {}).get('sections', [])
                )
                if self.verbose:
                    print(f"   ✨ In-love-and-unity image included: {has_unity_image}")
                if not has_unity_image:
                    issues.append("Missing required 'in-love-and-unity' signature image")
        
        # Check if videos were included when provided
        if 'videos' in extracted_data['assets'] and extracted_data['assets']['videos']:
            video_sections = [section for section in structured_data.get('content', {}).get('sections', []) 
                            if section.get('type') == 'video']
            if not video_sections:
                issues.append("Missing required video sections from provided assets")
        
        # Check if publish date was used correctly
        expected_date = extracted_data['publish_date']
        actual_date = structured_data.get('metadata', {}).get('publishDate')
        if actual_date != expected_date:
            issues.append(f"Incorrect publish date: expected {expected_date}, got {actual_date}")
        
        return len(issues) == 0, issues

    def create_iteration_prompt(self, original_response, issues, extracted_data):
        """Create a prompt for Claude to fix identified issues"""
        issues_text = '\n'.join([f"- {issue}" for issue in issues])
        
        return f"""Please review and fix the following issues in your previous blog post JSON response:

## Issues Found:
{issues_text}

## Original Response:
{original_response}

## Available Assets (for reference):
{json.dumps(extracted_data['assets'], indent=2)}

Please provide the corrected JSON blog post structure, ensuring all issues are addressed. Make sure to:
1. Include ALL required elements from the assets
2. Use the correct publish date: {extracted_data['publish_date']}
3. Follow the original content structure and requirements

Return only the corrected JSON response."""

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
            
            # Check if we need to add a featured video section at the top
            featured_video_html = ""
            has_video = False
            
            # Check if there are video sections in the content (Claude creates these now)
            video_sections = [section for section in content.get('sections', []) 
                            if section.get('type') == 'video' and 
                            section.get('content', {}).get('url') and 
                            section['content']['url'].strip() and 
                            not section['content']['url'].startswith('**')]
            
            if video_sections:
                has_video = True
                # Find the featured video (should be order: 0 or the first one)
                featured_video = min(video_sections, key=lambda x: x.get('order', 999))
                video_url = featured_video['content']['url']
                
                # Convert YouTube URL to embed format
                if 'youtube.com/watch?v=' in video_url:
                    video_id = video_url.split('watch?v=')[1].split('&')[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                elif 'youtu.be/' in video_url:
                    video_id = video_url.split('youtu.be/')[1].split('?')[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                else:
                    embed_url = video_url
                
                featured_video_html = f"""
                <!-- Featured Video -->
                <section class="featured-video">
                    <div class="container">
                        <div class="video-container">
                            <div class="video-embed">
                                <iframe src="{embed_url}" frameborder="0" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
                            </div>
                        </div>
                    </div>
                </section>
"""
                
                # Remove the featured video from content sections to avoid duplication
                content['sections'] = [section for section in content.get('sections', []) 
                                     if not (section.get('type') == 'video' and 
                                           section.get('content', {}).get('url') == video_url)]
            
            # If no video, add a placeholder
            if not has_video:
                featured_video_html = f"""
                <!-- Featured Video Placeholder -->
                <section class="featured-video">
                    <div class="container">
                        <div class="video-container">
                            <div class="video-placeholder">
                                <div class="placeholder-content">
                                    <div class="placeholder-icon">🎬</div>
                                    <h3 class="placeholder-title">Featured Video Coming Soon</h3>
                                    <p class="placeholder-text">We're working on creating an engaging video for this post. Check back soon!</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
"""
            
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
                    # Handle both 'src' and 'url' fields for backward compatibility
                    image_url = section['content'].get('src') or section['content'].get('url')
                    if image_url:
                        # Handle different image paths
                        if not image_url.startswith(('http://', 'https://', '/')):
                            # Check if it's the in-love-and-unity image (special case)
                            if 'in-love-and-unity' in image_url:
                                image_url = f"../assets/images/profiles/in-love-and-unity.png"
                            else:
                                image_url = f"../assets/images/blog/{image_url}"
                        
                        alt_text = section['content'].get('alt', metadata['title'])
                        caption = section['content'].get('caption', '')
                        
                        sections_html += f"""
                <div class="image-section">
                    <div class="content-image">
                        <img src="{image_url}" alt="{alt_text}" class="section-img">
                        {f'<p class="image-caption">{caption}</p>' if caption else ''}
                    </div>
                </div>
"""
                elif section['type'] == 'video':
                    video_url = section['content'].get('url', '')
                    video_title = section['content'].get('title', '')
                    video_description = section['content'].get('description', '')
                    
                    # Convert YouTube URL to embed format
                    if 'youtube.com/watch?v=' in video_url:
                        video_id = video_url.split('watch?v=')[1].split('&')[0]
                        embed_url = f"https://www.youtube.com/embed/{video_id}"
                    elif 'youtu.be/' in video_url:
                        video_id = video_url.split('youtu.be/')[1].split('?')[0]
                        embed_url = f"https://www.youtube.com/embed/{video_id}"
                    else:
                        embed_url = video_url  # Use as-is for other video platforms
                    
                    sections_html += f"""
                <div class="video-section">
                    {f'<h3 class="video-title">{video_title}</h3>' if video_title else ''}
                    <div class="video-embed">
                        <iframe src="{embed_url}" frameborder="0" allowfullscreen></iframe>
                    </div>
                    {f'<p class="video-description">{video_description}</p>' if video_description else ''}
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

        /* Featured Video */
        .featured-video {{
            padding: 60px 0;
            background: rgba(0, 0, 0, 0.2);
        }}

        .video-container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        .featured-video .video-embed {{
            position: relative;
            width: 100%;
            height: 0;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}

        .featured-video .video-embed iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}

        /* Video Placeholder */
        .video-placeholder {{
            background: linear-gradient(135deg, rgba(15, 15, 35, 0.9), rgba(45, 27, 105, 0.8));
            border: 2px dashed rgba(251, 191, 36, 0.3);
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}

        .placeholder-content {{
            max-width: 400px;
            margin: 0 auto;
        }}

        .placeholder-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
            filter: grayscale(30%);
        }}

        .placeholder-title {{
            color: #fbbf24;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 15px;
        }}

        .placeholder-text {{
            color: #d1d5db;
            font-size: 1.1rem;
            line-height: 1.6;
            opacity: 0.8;
        }}


        /* Post Content */
        .post-content {{
            padding: 80px 0;
            background: linear-gradient(rgba(15, 15, 35, 0.85), rgba(45, 27, 105, 0.9)), url('../assets/images/blog/{metadata['coverImage']}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            position: relative;
        }}

        .post-content::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.4);
            pointer-events: none;
        }}

        .content-wrapper {{
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }}

        .intro-section {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-left: 4px solid #fbbf24;
            padding: 30px;
            margin-bottom: 60px;
            border-radius: 10px;
            font-style: italic;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .intro-text {{
            font-size: 1.3rem;
            color: #e5e7eb;
            line-height: 1.7;
        }}

        .content-section {{
            margin-bottom: 60px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
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
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border-left: 4px solid #fbbf24;
            padding: 40px;
            margin: 40px 0;
            border-radius: 15px;
            font-style: italic;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.3);
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

        /* Special styling for in-love-and-unity image */
        .section-img[src*="in-love-and-unity"] {{
            max-width: 300px;
            margin: 0 auto;
            display: block;
        }}

        .image-caption {{
            text-align: center;
            color: #9ca3af;
            font-size: 0.9rem;
            margin-top: 15px;
            font-style: italic;
        }}

        .video-section {{
            margin: 40px 0;
            text-align: center;
        }}

        .video-embed {{
            position: relative;
            width: 100%;
            height: 0;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 15px 35px -10px rgba(139, 92, 246, 0.3);
        }}

        .video-embed iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}

        .video-title {{
            color: #fbbf24;
            font-size: 1.2rem;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .video-description {{
            color: #9ca3af;
            font-size: 0.9rem;
            margin-top: 15px;
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
            .post-content {{ background-attachment: scroll; }}
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
{featured_video_html}
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
    
    def update_blog_data_js(self, structured_data):
        """Update the blog-data.js file to include the new blog post"""
        try:
            blog_data_file = self.content_dir.parent / "assets" / "js" / "blog-data.js"
            
            # Read existing blog data
            with open(blog_data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract existing blog posts array
            import re
            array_match = re.search(r'const blogPostsData = \[(.*?)\];', content, re.DOTALL)
            if not array_match:
                print("❌ Could not find blogPostsData array in blog-data.js")
                return False
            
            # Create new blog post entry
            metadata = structured_data['metadata']
            
            # Check for existing entries with same slug FIRST
            existing_slug_pattern = f'slug: "{metadata["slug"]}"'
            if existing_slug_pattern in content:
                print(f"⚠️  Found existing entry with slug '{metadata['slug']}' in blog-data.js")
                print("   Skipping blog-data.js update to avoid duplicates")
                return True  # Return True since this isn't an error, just preventing duplicates
            
            # Get the highest existing ID
            id_matches = re.findall(r'id:\s*(\d+)', content)
            max_id = max([int(id_match) for id_match in id_matches]) if id_matches else 0
            new_id = max_id + 1
            
            # Format tags for JavaScript
            tags_js = ', '.join([f'"{tag}"' for tag in metadata['tags']])
            
            new_post_entry = f'''    {{
        id: {new_id},
        title: "{metadata['title']}",
        excerpt: "{metadata['excerpt']}",
        image: "assets/images/blog/{metadata['coverImage']}",
        date: "{metadata['publishDate']}",
        slug: "{metadata['slug']}",
        tags: [{tags_js}],
        content: {{
            subtitle: "{metadata['excerpt']}",
            intro: "{structured_data['content']['sections'][0]['content']['text'] if structured_data['content']['sections'] else ''}",
            sections: []
        }}
    }},'''
            
            # Insert the new post at the beginning of the array (after the opening bracket)
            array_start = content.find('const blogPostsData = [') + len('const blogPostsData = [')
            new_content = (content[:array_start] + '\n' + new_post_entry + 
                         content[array_start:])
            
            # Write back to file
            with open(blog_data_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Blog data updated: {blog_data_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating blog-data.js: {e}")
            return False
    
    def check_existing_post(self, slug, publish_date):
        """Check if a blog post already exists based on slug or title similarity"""
        try:
            # Check for exact slug match in published directories
            expected_dir_name = f"{publish_date}_{slug}"
            expected_path = self.output_dir / expected_dir_name
            
            if expected_path.exists():
                return {'exists': True, 'path': expected_path, 'type': 'exact_match'}
            
            # Check for similar slugs (in case of slight variations)
            for dir_path in self.output_dir.iterdir():
                if dir_path.is_dir():
                    dir_name = dir_path.name
                    # Extract slug from directory name (format: YYYY-MM-DD_slug)
                    if '_' in dir_name:
                        existing_slug = '_'.join(dir_name.split('_')[1:])
                        # Check for similarity (same words, different formatting)
                        if self._slugs_similar(slug, existing_slug):
                            return {'exists': True, 'path': dir_path, 'type': 'similar_match'}
            
            # Check in blog-data.js for entries
            blog_data_file = self.content_dir.parent / "assets" / "js" / "blog-data.js"
            if blog_data_file.exists():
                with open(blog_data_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f'slug: "{slug}"' in content:
                        return {'exists': True, 'path': blog_data_file, 'type': 'blog_data_exact_match'}
                    
                    # Also check for similar slugs in blog data
                    import re
                    existing_slugs = re.findall(r'slug: "([^"]+)"', content)
                    for existing_slug in existing_slugs:
                        if self._slugs_similar(slug, existing_slug):
                            return {'exists': True, 'path': blog_data_file, 'type': 'blog_data_similar_match'}
            
            return {'exists': False}
            
        except Exception as e:
            print(f"❌ Error checking existing post: {e}")
            return {'exists': False}
    
    def _slugs_similar(self, slug1, slug2):
        """Check if two slugs are similar (same core words)"""
        # Normalize slugs: remove extra hyphens, convert underscores
        def normalize_slug(slug):
            return slug.replace('_', '-').replace('--', '-').strip('-').lower()
        
        norm_slug1 = normalize_slug(slug1)
        norm_slug2 = normalize_slug(slug2)
        
        # Check if they're the same after normalization
        if norm_slug1 == norm_slug2:
            return True
        
        # Check if the core words are the same (allowing for minor variations)
        words1 = set(norm_slug1.split('-'))
        words2 = set(norm_slug2.split('-'))
        
        # If more than 70% of words overlap, consider them similar
        if len(words1.intersection(words2)) / max(len(words1), len(words2)) > 0.7:
            return True
        
        return False
    
    def process_file(self, filename_or_path):
        """Fully automated processing of a raw input file"""
        process_start = time.time()
        
        # Handle both relative filenames and absolute/relative paths
        file_path = Path(filename_or_path)
        if not file_path.is_absolute():
            # If it's just a filename without path separators, use raw_input_dir
            if '/' not in str(filename_or_path) and '\\' not in str(filename_or_path):
                file_path = self.raw_input_dir / filename_or_path
            # Otherwise, treat it as a relative path from current directory
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        print(f"\n🔄 Processing: {file_path.name}")
        self.log_time(f"Starting processing for {file_path.name}")
        print("=" * 60)
        
        # Step 1: Extract content and assets
        print("\n📖 Step 1: Extracting content and assets...")
        step_start = time.time()
        extracted_data = self.extract_content_and_assets(file_path)
        self.log_time("Content extraction complete", step_start)
        print(f"   Title: {extracted_data['title']}")
        print(f"   Assets: {len(extracted_data.get('assets', {}))}")
        print(f"   Content length: {len(extracted_data['main_content'])} chars")
        
        # Step 2: Create processing prompt
        print("\n📝 Step 2: Creating processing prompt...")
        step_start = time.time()
        prompt = self.create_processing_prompt(extracted_data)
        self.log_time("Prompt creation complete", step_start)
        
        # Step 3: Call Claude Code with iteration
        print("\n🤖 Step 3: Calling Claude Code for processing...")
        print("   ⏳ This may take 30-120 seconds depending on content complexity...")
        step_start = time.time()
        
        structured_data = None
        current_prompt = prompt
        
        for iteration in range(1, self.max_iterations + 1):
            if iteration > 1:
                print(f"\n🔄 Iteration {iteration}: Fixing identified issues...")
            
            response = self.call_claude_code(current_prompt)
            if not response:
                print("❌ Failed to get response from Claude Code")
                return None
            
            # Step 4: Extract JSON from response
            if iteration == 1:
                print("\n🔍 Step 4: Extracting JSON from response...")
            structured_data = self.extract_json_from_response(response)
            
            if not structured_data:
                print("❌ Failed to extract valid JSON from response")
                if iteration == self.max_iterations:
                    return None
                continue
            
            # Step 4.5: Validate response
            if self.verbose:
                print(f"   🔍 Validating Claude response (iteration {iteration})...")
                print(f"   📋 Available assets: {extracted_data['assets']}")
            is_valid, issues = self.validate_claude_response(structured_data, extracted_data)
            
            if is_valid:
                if iteration > 1:
                    print(f"✅ Issues resolved after {iteration} iterations")
                break
            else:
                print(f"⚠️  Validation issues found (iteration {iteration}):")
                for issue in issues:
                    print(f"   - {issue}")
                
                if iteration == self.max_iterations:
                    print(f"⚠️  Max iterations ({self.max_iterations}) reached. Proceeding with current result.")
                    break
                
                # Create iteration prompt for next attempt
                current_prompt = self.create_iteration_prompt(response, issues, extracted_data)
        
        self.log_time("Claude Code processing complete", step_start)
        
        if not structured_data:
            print("❌ Failed to extract valid JSON from response")
            return None
        
        # Step 5: Check for existing posts (duplicate detection)
        print("\n🔍 Step 5: Checking for existing posts...")
        step_start = time.time()
        slug = structured_data['metadata']['slug']
        publish_date = structured_data['metadata']['publishDate']
        existing_check = self.check_existing_post(slug, publish_date)
        self.log_time("Duplicate check complete", step_start)
        
        if existing_check['exists']:
            print(f"📝 Found existing post: {existing_check['type']}")
            print(f"📁 Location: {existing_check['path']}")
            
            # Check if auto-update is enabled
            if self.auto_update:
                print("🔄 Auto-update enabled - updating existing post...")
                action = 'u'
            else:
                # Ask user what to do
                action = input("Choose action - (u)pdate existing, (s)kip, or (f)orce create new: ").lower().strip()
            
            if action == 's':
                print("⏭️  Skipping - post already exists")
                return {'action': 'skipped', 'existing_path': existing_check['path']}
            elif action == 'u':
                if not self.auto_update:
                    print("🔄 Updating existing post...")
                # Continue with update process
            elif action == 'f':
                print("🚀 Force creating new post...")
                # Continue with creation process
            else:
                print("❌ Invalid choice, skipping...")
                return {'action': 'skipped', 'existing_path': existing_check['path']}
        
        # Step 6: Save the structured post (JSON)
        print("\n💾 Step 6: Saving structured blog post JSON...")
        step_start = time.time()
        base_filename = file_path.stem
        post_file = self.save_structured_post(structured_data, base_filename)
        self.log_time("JSON save complete", step_start)
        
        if not post_file:
            print("❌ Failed to save JSON structure")
            return None
        
        # Step 7: Generate and save HTML blog post
        print("\n🎨 Step 7: Generating beautiful HTML blog post...")
        step_start = time.time()
        html_file = self.save_html_blog_post(structured_data, base_filename)
        self.log_time("HTML generation complete", step_start)
        
        if not html_file:
            print("⚠️  JSON saved but HTML generation failed")
            return {'json': post_file, 'html': None}
        
        # Step 8: Update blog explorer data
        print("\n📋 Step 8: Adding post to blog explorer...")
        step_start = time.time()
        blog_data_updated = self.update_blog_data_js(structured_data)
        self.log_time("Blog explorer update complete", step_start)
        
        print("\n" + "=" * 60)
        total_time = time.time() - process_start
        print("🎉 SUCCESS! Complete blog automation pipeline finished!")
        print(f"⏱️  Total processing time: {total_time:.1f} seconds")
        print(f"📁 JSON Location: {post_file}")
        print(f"🌐 HTML Location: {html_file}")
        print(f"📋 Blog Explorer: {'✅ Updated' if blog_data_updated else '❌ Failed'}")
        print(f"📝 Title: {structured_data['metadata']['title']}")
        print(f"🏷️  Tags: {', '.join(structured_data['metadata']['tags'])}")
        print(f"🔗 Blog URL: blog/post-{structured_data['metadata']['slug']}.html")
        return {
            'json': post_file, 
            'html': html_file, 
            'blog_data_updated': blog_data_updated
        }
        
        return None
    
    def refresh_blog_explorer(self):
        """Rebuild the entire blog-data.js from all published posts"""
        try:
            print("🔄 Refreshing blog explorer from all published posts...")
            
            # Find all published post directories
            published_posts = []
            if self.output_dir.exists():
                for post_dir in self.output_dir.iterdir():
                    if post_dir.is_dir() and (post_dir / "post.json").exists():
                        try:
                            with open(post_dir / "post.json", 'r', encoding='utf-8') as f:
                                post_data = json.loads(f.read())
                                published_posts.append(post_data)
                                print(f"   📄 Found: {post_data['metadata']['title']}")
                        except Exception as e:
                            print(f"   ⚠️  Error reading {post_dir}/post.json: {e}")
            
            if not published_posts:
                print("❌ No published posts found!")
                return False
            
            # Sort posts by date (newest first)
            published_posts.sort(key=lambda x: x['metadata']['publishDate'], reverse=True)
            
            # Generate blog data entries
            blog_entries = []
            for i, post_data in enumerate(published_posts, 1):
                metadata = post_data['metadata']
                content = post_data.get('content', {})
                
                # Get first section intro or first paragraph
                intro = ""
                if 'sections' in content and content['sections']:
                    first_section = content['sections'][0]
                    if first_section.get('type') == 'intro':
                        intro = first_section['content']['text']
                    elif first_section.get('type') == 'text' and 'paragraphs' in first_section.get('content', {}):
                        intro = first_section['content']['paragraphs'][0]
                
                # Format tags for JavaScript
                tags_js = ', '.join([f'"{tag}"' for tag in metadata['tags']])
                
                # Escape quotes and newlines for JavaScript
                def js_escape(text):
                    if not text:
                        return ""
                    return text.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                
                title_escaped = js_escape(metadata['title'])
                excerpt_escaped = js_escape(metadata['excerpt'])
                intro_escaped = js_escape(intro[:200] + ('...' if len(intro) > 200 else ''))
                
                entry = f'''    {{
        id: {i},
        title: "{title_escaped}",
        excerpt: "{excerpt_escaped}",
        image: "assets/images/blog/{metadata['coverImage']}",
        date: "{metadata['publishDate']}",
        slug: "{metadata['slug']}",
        tags: [{tags_js}],
        content: {{
            subtitle: "{excerpt_escaped}",
            intro: "{intro_escaped}",
            sections: []
        }}
    }}'''
                blog_entries.append(entry)
            
            # Create the complete blog-data.js content
            entries_joined = ',\n'.join(blog_entries)
            blog_data_content = f'''// Blog Posts Data Structure
// This file contains blog posts data for the multisensory blog experience
// Updated automatically by the Claude Blog Processor

const blogPostsData = [
{entries_joined}
];

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = blogPostsData;
}}'''
            
            # Write the new blog-data.js file
            blog_data_file = self.content_dir.parent / "assets" / "js" / "blog-data.js"
            with open(blog_data_file, 'w', encoding='utf-8') as f:
                f.write(blog_data_content)
            
            print(f"✅ Blog explorer refreshed with {len(published_posts)} posts!")
            return True
            
        except Exception as e:
            print(f"❌ Error refreshing blog explorer: {e}")
            return False

def main():
    """Main execution function"""
    print("🚀 Fully Automated Claude Code Blog Processor")
    print("Uses OAUTH token for complete automation - no manual steps!\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python automated_claude_processor.py <path-to-file.md> [--auto-update]")
        print("  python automated_claude_processor.py --refresh-blog-explorer")
        print("\nExamples:")
        print("  python automated_claude_processor.py why.md                    # File in raw-input/")
        print("  python automated_claude_processor.py raw-input/why.md         # Relative path")
        print("  python automated_claude_processor.py /full/path/to/post.md    # Absolute path")
        print("  python automated_claude_processor.py test-post.md --auto-update")
        print("  python automated_claude_processor.py --refresh-blog-explorer")
        print("\nFlags:")
        print("  --auto-update           Automatically update existing posts without prompting")
        print("  --refresh-blog-explorer Rebuild blog-data.js from all published posts")
        print("\nMake sure CLAUDE_CODE_OAUTH_TOKEN environment variable is set!")
        return
    
    # Check for special modes
    if '--refresh-blog-explorer' in sys.argv:
        processor = AutomatedClaudeProcessor(verbose=True, auto_update=False)
        success = processor.refresh_blog_explorer()
        if success:
            print("\n✅ Blog explorer refresh complete!")
        else:
            print("\n❌ Blog explorer refresh failed!")
        return
    
    # Check for auto-update flag
    auto_update = '--auto-update' in sys.argv
    
    processor = AutomatedClaudeProcessor(verbose=True, auto_update=auto_update)
    filename = sys.argv[1]
    
    result = processor.process_file(filename)
    
    if result:
        print(f"\n✅ Automation complete! Your blog post is ready.")
    else:
        print(f"\n❌ Automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()