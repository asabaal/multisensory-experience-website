-- Row Level Security Policies Migration
-- Run this after the initial setup to configure security

-- Enable RLS on all tables
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_post_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE authors ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_sections ENABLE ROW LEVEL SECURITY;

-- Public read policies
CREATE POLICY "Public can view published posts" ON blog_posts
    FOR SELECT USING (published = true);

CREATE POLICY "Public can view tags" ON tags
    FOR SELECT USING (true);

CREATE POLICY "Public can view post tags" ON blog_post_tags
    FOR SELECT USING (true);

CREATE POLICY "Public can view authors" ON authors
    FOR SELECT USING (true);

CREATE POLICY "Public can view content sections" ON content_sections
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM blog_posts 
            WHERE blog_posts.id = content_sections.post_id 
            AND blog_posts.published = true
        )
    );