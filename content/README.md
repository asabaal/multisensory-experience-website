# Blog Content Management System

This directory contains all blog content in a structured, organized format.

## Directory Structure
```
content/
├── blog/                    ← All blog posts
│   ├── drafts/             ← Unpublished posts
│   └── published/          ← Published posts
│       ├── 2024-05-12_embracing-the-age-of-creativity/
│       │   ├── post.json   ← Post metadata & content
│       │   ├── cover.jpg   ← Cover image
│       │   └── assets/     ← Additional images/files
│       └── ...
├── templates/              ← Content templates
│   ├── post-template.json
│   └── section-templates.json
└── images/                 ← Shared blog images
    ├── covers/
    ├── content/
    └── profiles/
```

## Post Structure
Each blog post directory contains:
- `post.json` - All post data in structured format
- `cover.jpg/png` - Cover image
- `assets/` - Any additional images or files

## Content Format
Posts are stored as JSON with this structure:
```json
{
  "metadata": {
    "title": "Post Title",
    "slug": "post-slug",
    "publishDate": "2024-05-12",
    "tags": ["tag1", "tag2"],
    "excerpt": "Post summary..."
  },
  "content": {
    "sections": [
      {
        "type": "intro",
        "content": "Introduction text..."
      },
      {
        "type": "quote", 
        "content": {
          "text": "Quote text",
          "author": "Author"
        }
      }
    ]
  }
}
```

## Usage
- ✅ Local editing and organization
- ✅ Version control ready (optional)
- ✅ Easy migration to Supabase
- ✅ Supports rich content structure
- ✅ Asset management included