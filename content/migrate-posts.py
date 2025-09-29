#!/usr/bin/env python3
"""
Blog Content Migration Script
Helps migrate blog posts from external directory structure to new organized format
"""

import os
import json
import shutil
from pathlib import Path
import re
from datetime import datetime

# Configuration
EXTERNAL_BLOG_DIR = "/mnt/d/Work/Asabaal Ventures/Blog"
CONTENT_DIR = "./content/blog"
PUBLISHED_DIR = f"{CONTENT_DIR}/published"
ASSETS_DIR = "./assets/images/blog"

def parse_directory_name(dir_name):
    """Parse directory name to extract slug and date"""
    # Format: {slug}_{date}
    parts = dir_name.split('_')
    if len(parts) >= 2:
        date = parts[-1]  # Last part should be date
        slug = '_'.join(parts[:-1])  # Everything else is slug
        return slug, date
    return dir_name, None

def create_post_json_template(title, slug, date, tags=None):
    """Create a basic post.json template"""
    return {
        "metadata": {
            "title": title.replace('_', ' ').title(),
            "slug": slug,
            "publishDate": date if date else "2024-01-01",
            "tags": tags or ["General"],
            "excerpt": "Add your post excerpt here...",
            "coverImage": "cover.jpg",
            "featured": False,
            "status": "draft"
        },
        "content": {
            "subtitle": "Add your subtitle here...",
            "sections": [
                {
                    "type": "intro",
                    "content": {
                        "text": "Add your introduction here..."
                    },
                    "order": 1
                }
            ]
        },
        "author": {
            "name": "Asabaal Horan",
            "signature": "In love and unity,<br><strong>Asabaal Horan</strong><br>Founder, Asabaal Ventures"
        }
    }

def migrate_posts():
    """Migrate posts from external directory"""
    
    if not os.path.exists(EXTERNAL_BLOG_DIR):
        print(f"❌ External blog directory not found: {EXTERNAL_BLOG_DIR}")
        return
    
    # Create directories
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    os.makedirs(f"{CONTENT_DIR}/drafts", exist_ok=True)
    
    print(f"🔍 Scanning {EXTERNAL_BLOG_DIR} for blog posts...")
    
    migrated_count = 0
    
    for item in os.listdir(EXTERNAL_BLOG_DIR):
        item_path = os.path.join(EXTERNAL_BLOG_DIR, item)
        
        # Skip files, only process directories
        if not os.path.isdir(item_path):
            continue
            
        # Skip common non-post directories
        if item in ['Banners', 'assets', 'images']:
            continue
            
        print(f"📝 Processing: {item}")
        
        # Parse directory name
        slug, date = parse_directory_name(item)
        
        # Format date properly
        if date and len(date) == 8:  # YYYYMMDD format
            try:
                date_obj = datetime.strptime(date, "%Y%m%d")
                date = date_obj.strftime("%Y-%m-%d")
            except:
                date = "2024-01-01"
        elif not date:
            date = "2024-01-01"
        
        # Create new directory name
        new_dir_name = f"{date}_{slug}"
        new_post_dir = os.path.join(PUBLISHED_DIR, new_dir_name)
        
        # Create the new post directory
        os.makedirs(new_post_dir, exist_ok=True)
        
        # Create post.json template
        post_data = create_post_json_template(
            title=slug.replace('_', ' ').title(),
            slug=slug.replace('_', '-'),
            date=date
        )
        
        # Save post.json
        with open(os.path.join(new_post_dir, 'post.json'), 'w', encoding='utf-8') as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)
        
        # Create assets directory
        assets_dir = os.path.join(new_post_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Copy any images from the original directory
        for file in os.listdir(item_path):
            file_path = os.path.join(item_path, file)
            if os.path.isfile(file_path) and file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                # Copy to assets folder
                shutil.copy2(file_path, assets_dir)
                print(f"  📷 Copied image: {file}")
        
        print(f"  ✅ Created: {new_dir_name}")
        migrated_count += 1
    
    print(f"\n🎉 Migration complete! Processed {migrated_count} posts")
    print(f"📁 Posts are now in: {PUBLISHED_DIR}")
    print("\n📝 Next steps:")
    print("1. Review each post.json file and add proper content")
    print("2. Add cover images (rename to cover.jpg)")
    print("3. Update metadata (title, excerpt, tags)")
    print("4. Add proper content sections")

def clean_up_external():
    """Optional: Clean up the external directory after migration"""
    response = input(f"\n🗑️  Do you want to remove the external blog directory ({EXTERNAL_BLOG_DIR})? (y/N): ")
    if response.lower() == 'y':
        try:
            shutil.rmtree(EXTERNAL_BLOG_DIR)
            print(f"✅ Removed: {EXTERNAL_BLOG_DIR}")
        except Exception as e:
            print(f"❌ Error removing directory: {e}")
    else:
        print("📁 External directory preserved")

if __name__ == "__main__":
    print("🚀 Blog Content Migration Tool")
    print("=" * 40)
    
    migrate_posts()
    
    # Ask about cleanup
    clean_up_external()