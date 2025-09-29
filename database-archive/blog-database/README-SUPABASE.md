# Supabase Blog Backend Setup

This document explains how to set up the Supabase backend for your multisensory blog.

## Quick Start

1. **Create a Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note your project URL and anon key

2. **Run Database Migrations**
   - In your Supabase dashboard, go to SQL Editor
   - Run the migration files in order:
     1. `supabase/migrations/001_initial_setup.sql`
     2. `supabase/migrations/002_rls_policies.sql`
     3. `supabase/migrations/003_views_functions.sql`
     4. `supabase/seed_data.sql` (optional - adds sample data)

3. **Configure Your Site**
   - Copy `.env.example` to `.env`
   - Update `config/supabase-config.js` with your project details
   - Replace `your-project-id` and `your-anon-key-here` with actual values

## Database Structure

### Tables Created

- **authors**: Blog authors/users
- **blog_posts**: Main blog posts table
- **tags**: Post tags/categories
- **blog_post_tags**: Many-to-many relationship between posts and tags
- **content_sections**: Modular content sections for posts

### Views Created

- **blog_posts_with_details**: Posts with author info and tags included

### Functions Created

- **get_post_with_content()**: Retrieves a post with all content sections
- **increment_post_views()**: Increments view count for analytics

## Features Included

✅ **Public Blog Reading**: Anyone can read published posts  
✅ **Responsive Data Structure**: Handles complex blog content  
✅ **SEO Optimization**: Meta titles, descriptions, and URLs  
✅ **View Tracking**: Post view analytics  
✅ **Tag System**: Categorization and filtering  
✅ **Modular Content**: Flexible content sections  
✅ **Row Level Security**: Secure data access  
✅ **Fallback Support**: Works with or without Supabase

## Configuration Files

- `supabase/schema.sql` - Complete database schema
- `supabase/migrations/` - Step-by-step migration files
- `supabase/seed_data.sql` - Sample data including your first blog post
- `config/supabase-config.js` - Frontend configuration
- `assets/js/supabase-client.js` - JavaScript client for API calls

## Usage

The blog will automatically try to use Supabase if configured, otherwise fallback to local data. This means:

1. **With Supabase**: Dynamic content from database
2. **Without Supabase**: Static content from `blog-data.js`

## Next Steps

1. **Set up your Supabase project** using the migration files
2. **Update configuration** with your project credentials  
3. **Test the blog** - it should load posts from Supabase
4. **Add more posts** through the Supabase dashboard or build an admin interface

## Security Notes

- Keep your service role key secure (not in frontend code)
- Row Level Security is enabled by default
- Only published posts are visible to public users
- All sensitive operations require proper authentication

## Troubleshooting

- Check browser console for connection errors
- Verify your Supabase URL and keys are correct
- Ensure RLS policies are set up properly
- Test database functions in Supabase SQL editor first