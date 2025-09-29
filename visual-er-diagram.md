# Visual ER Diagrams for Blog Database

## Option 1: Single Table (ULTRA SIMPLE)
```
    ╔═══════════════════════════════════════╗
    ║              BLOG_POSTS               ║
    ╠═══════════════════════════════════════╣
    ║ 🔑 id (UUID)                          ║
    ║ 📝 title                              ║
    ║ 🔗 slug (unique)                      ║
    ║ 📄 excerpt                            ║
    ║ 🖼️  cover_image_url                   ║
    ║ 🌐 content_html (full HTML)           ║
    ║ 🏷️  tags (comma-separated)            ║
    ║ ✅ published                          ║
    ║ 📅 published_date                     ║
    ║ ⏰ created_at                         ║
    ╚═══════════════════════════════════════╝
```

## Option 2: Two Tables (RECOMMENDED)
```
    ╔═══════════════════════════════════════╗
    ║              BLOG_POSTS               ║
    ╠═══════════════════════════════════════╣
    ║ 🔑 id (UUID)                          ║
    ║ 📝 title                              ║
    ║ 🔗 slug (unique)                      ║
    ║ 📄 excerpt                            ║
    ║ 🖼️  cover_image_url                   ║
    ║ 🏷️  tags (JSON array)                 ║
    ║ ✅ published                          ║
    ║ 📅 published_date                     ║
    ║ ⏰ created_at                         ║
    ╚═══════════════════════════════════════╝
                        │
                        │ 1:Many
                        │ (one post has many content sections)
                        ▼
    ╔═══════════════════════════════════════╗
    ║            POST_CONTENT               ║
    ╠═══════════════════════════════════════╣
    ║ 🔑 id (UUID)                          ║
    ║ 🔗 post_id (FK → blog_posts.id)       ║
    ║ 📋 section_type                       ║
    ║    ("intro", "text", "quote", etc.)   ║
    ║ 📦 content (JSON)                     ║
    ║    {flexible based on section_type}   ║
    ║ 🔢 order_index                        ║
    ╚═══════════════════════════════════════╝
```

## Sample Section Types & Content
```
📝 TEXT SECTION:
{
  "section_type": "text",
  "content": {
    "title": "The Transformation Moment",
    "paragraphs": ["I've long yearned...", "As a highly educated..."]
  }
}

💬 QUOTE SECTION:
{
  "section_type": "quote", 
  "content": {
    "text": "The Age of Creativity is upon us...",
    "author": ""
  }
}

📋 LIST SECTION:
{
  "section_type": "list",
  "content": {
    "title": "Topics we'll explore:",
    "items": ["AI and creativity", "Building community", ...]
  }
}

🖼️ IMAGE SECTION:
{
  "section_type": "image",
  "content": {
    "url": "assets/images/blog/logo.jpg",
    "alt": "Age of Creativity Logo",
    "caption": "Our new logo design"
  }
}
```

## Queries You'll Need (Simple!)
```sql
-- Get all published posts for blog page
SELECT * FROM blog_posts WHERE published = true ORDER BY published_date DESC;

-- Get single post with all content
SELECT 
  bp.*,
  JSON_AGG(pc.* ORDER BY pc.order_index) as content_sections
FROM blog_posts bp
LEFT JOIN post_content pc ON bp.id = pc.post_id  
WHERE bp.slug = 'your-post-slug'
GROUP BY bp.id;

-- Search posts by tag (using JSON array)
SELECT * FROM blog_posts 
WHERE published = true 
AND tags @> '["AI"]'::jsonb;
```

## Storage Requirements
- **Small blog (26 posts)**: ~1-5MB total
- **Images**: Store URLs, actual images in Supabase Storage
- **Content**: JSON is efficient and flexible

**Bottom line: 2 tables, ~5 columns each, dead simple!**

Which option feels right to you?