#!/usr/bin/env python3
"""
Debug test for OpenRouter Qwen3 processor
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("🧪 Testing basic functionality...")
    
    # Check directories
    content_dir = Path(__file__).parent
    raw_input_dir = content_dir / "raw-input"
    output_dir = content_dir / "blog" / "published"
    template_path = content_dir / "templates" / "post-template.json"
    
    print(f"Content dir: {content_dir}")
    print(f"Raw input dir: {raw_input_dir}")
    print(f"Output dir: {output_dir}")
    print(f"Template path: {template_path}")
    
    # Check if directories exist
    if not raw_input_dir.exists():
        print(f"❌ Raw input directory doesn't exist: {raw_input_dir}")
        return False
    
    if not output_dir.exists():
        print(f"❌ Output directory doesn't exist: {output_dir}")
        return False
    
    if not template_path.exists():
        print(f"❌ Template doesn't exist: {template_path}")
        return False
    
    # Check for markdown files
    markdown_files = list(raw_input_dir.glob("*.md"))
    print(f"📝 Found {len(markdown_files)} markdown files")
    
    if not markdown_files:
        print("❌ No markdown files found")
        return False
    
    # Check first file
    first_file = markdown_files[0]
    print(f"📄 First file: {first_file}")
    
    try:
        with open(first_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Successfully read file ({len(content)} characters)")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set")
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    print("✅ All basic checks passed!")
    return True

if __name__ == "__main__":
    if test_basic_functionality():
        print("\n🎉 Basic functionality test passed!")
    else:
        print("\n❌ Basic functionality test failed!")
        sys.exit(1)