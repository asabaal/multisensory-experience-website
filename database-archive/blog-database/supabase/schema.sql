-- Supabase Database Schema for Multisensory Blog
-- This schema supports the blog functionality with posts, tags, and content sections

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create blog_posts table
CREATE TABLE IF NOT EXISTS blog_posts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    excerpt TEXT,
    cover_image_url TEXT,
    content JSONB NOT NULL DEFAULT '{}',
    published BOOLEAN DEFAULT false,
    featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    author_id UUID,
    meta_title TEXT,
    meta_description TEXT,
    reading_time_minutes INTEGER,
    view_count INTEGER DEFAULT 0
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#8b5cf6',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create blog_post_tags junction table (many-to-many)
CREATE TABLE IF NOT EXISTS blog_post_tags (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    post_id UUID REFERENCES blog_posts(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(post_id, tag_id)
);

-- Create authors table (for future multi-author support)
CREATE TABLE IF NOT EXISTS authors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    bio TEXT,
    avatar_url TEXT,
    website_url TEXT,
    social_links JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create content_sections table for modular blog content
CREATE TABLE IF NOT EXISTS content_sections (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    post_id UUID REFERENCES blog_posts(id) ON DELETE CASCADE,
    section_type TEXT NOT NULL, -- 'text', 'quote', 'image', 'video', 'code', 'list'
    title TEXT,
    content JSONB NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add foreign key for author_id
ALTER TABLE blog_posts 
ADD CONSTRAINT fk_blog_posts_author 
FOREIGN KEY (author_id) REFERENCES authors(id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX IF NOT EXISTS idx_blog_posts_published ON blog_posts(published);
CREATE INDEX IF NOT EXISTS idx_blog_posts_featured ON blog_posts(featured);
CREATE INDEX IF NOT EXISTS idx_blog_posts_published_at ON blog_posts(published_at);
CREATE INDEX IF NOT EXISTS idx_blog_posts_author ON blog_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug);
CREATE INDEX IF NOT EXISTS idx_content_sections_post ON content_sections(post_id);
CREATE INDEX IF NOT EXISTS idx_content_sections_order ON content_sections(post_id, order_index);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_blog_posts_updated_at 
    BEFORE UPDATE ON blog_posts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_authors_updated_at 
    BEFORE UPDATE ON authors 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_post_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE authors ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_sections ENABLE ROW LEVEL SECURITY;

-- Allow public read access to published posts
CREATE POLICY "Public can view published posts" ON blog_posts
    FOR SELECT USING (published = true);

-- Allow public read access to tags
CREATE POLICY "Public can view tags" ON tags
    FOR SELECT USING (true);

-- Allow public read access to post-tag relationships
CREATE POLICY "Public can view post tags" ON blog_post_tags
    FOR SELECT USING (true);

-- Allow public read access to authors
CREATE POLICY "Public can view authors" ON authors
    FOR SELECT USING (true);

-- Allow public read access to content sections for published posts
CREATE POLICY "Public can view content sections" ON content_sections
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM blog_posts 
            WHERE blog_posts.id = content_sections.post_id 
            AND blog_posts.published = true
        )
    );

-- Create view for blog posts with tags and author info
CREATE OR REPLACE VIEW blog_posts_with_details AS
SELECT 
    bp.*,
    a.name as author_name,
    a.avatar_url as author_avatar,
    COALESCE(
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'id', t.id,
                'name', t.name,
                'slug', t.slug,
                'color', t.color
            )
        ) FILTER (WHERE t.id IS NOT NULL),
        '[]'::json
    ) as tags
FROM blog_posts bp
LEFT JOIN authors a ON bp.author_id = a.id
LEFT JOIN blog_post_tags bpt ON bp.id = bpt.post_id
LEFT JOIN tags t ON bpt.tag_id = t.id
GROUP BY bp.id, a.name, a.avatar_url;

-- Create function to get posts with full content
CREATE OR REPLACE FUNCTION get_post_with_content(post_slug TEXT)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT JSON_BUILD_OBJECT(
        'post', row_to_json(bp),
        'content_sections', COALESCE(
            JSON_AGG(
                JSON_BUILD_OBJECT(
                    'id', cs.id,
                    'section_type', cs.section_type,
                    'title', cs.title,
                    'content', cs.content,
                    'order_index', cs.order_index
                )
                ORDER BY cs.order_index
            ) FILTER (WHERE cs.id IS NOT NULL),
            '[]'::json
        )
    ) INTO result
    FROM blog_posts_with_details bp
    LEFT JOIN content_sections cs ON bp.id = cs.post_id
    WHERE bp.slug = post_slug AND bp.published = true
    GROUP BY bp.id, bp.title, bp.slug, bp.excerpt, bp.cover_image_url, 
             bp.content, bp.published, bp.featured, bp.created_at, 
             bp.updated_at, bp.published_at, bp.author_id, bp.meta_title, 
             bp.meta_description, bp.reading_time_minutes, bp.view_count,
             bp.author_name, bp.author_avatar, bp.tags;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;