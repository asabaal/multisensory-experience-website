# Blog Content Migration Guide

## What I've Set Up For You

✅ **New organized structure** in `content/` directory  
✅ **Template system** for consistent post formatting  
✅ **Migration script** to move your existing posts  
✅ **Gitignore configuration** with flexible options  

## Quick Migration Steps

1. **Run the migration script:**
   ```bash
   cd content/
   python3 migrate-posts.py
   ```

2. **What it does:**
   - ✅ Scans your `/mnt/d/Work/Asabaal Ventures/Blog` directory
   - ✅ Creates organized folders: `2024-05-12_embracing-the-age-of-creativity/`
   - ✅ Generates `post.json` templates for each post
   - ✅ Copies images to `assets/` folders
   - ✅ Creates proper directory structure

3. **After migration, you'll have:**
   ```
   content/blog/published/
   ├── 2024-05-12_embracing-the-age-of-creativity/
   │   ├── post.json          ← Your post content here
   │   ├── cover.jpg          ← Rename your cover image
   │   └── assets/            ← Additional images
   └── 2024-XX-XX_your-other-posts/
   ```

## New Workflow

### Creating a New Post
1. Copy `content/templates/post-template.json`
2. Create new directory: `content/blog/drafts/YYYY-MM-DD_your-slug/`
3. Edit the `post.json` with your content
4. Add cover image as `cover.jpg`
5. Move to `published/` when ready

### Content Structure Benefits
- ✅ **Organized**: Each post has its own folder
- ✅ **Structured**: JSON format for easy database migration
- ✅ **Asset management**: Images stay with their posts
- ✅ **Version control ready**: Can track changes if wanted
- ✅ **Database migration**: Easy to upload to Supabase

## Git Options (You Choose!)

I've set up three options in `.gitignore`:

1. **Track everything** (recommended for backup)
   - Uncomment: `# content/`
   
2. **Track published only** (current setup)
   - Keeps drafts private, publishes content in git
   
3. **Track nothing** 
   - Uncomment: `# content/blog/`
   - Keep all content local only

## Next Steps After Migration

1. **Review generated `post.json` files**
2. **Add proper content** to replace templates
3. **Add cover images** (rename to `cover.jpg`)
4. **Update metadata** (titles, excerpts, tags)
5. **Test with Supabase** - easy upload from JSON format

The migration script will preserve your images and create a clean structure. Your old directory can be deleted once you're happy with the migration!

Ready to run it?