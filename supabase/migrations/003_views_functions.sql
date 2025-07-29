-- Views and Functions Migration
-- Run this to create helpful views and functions

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

-- Function to get post with full content
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

-- Function to increment view count
CREATE OR REPLACE FUNCTION increment_post_views(post_slug TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE blog_posts 
    SET view_count = view_count + 1 
    WHERE slug = post_slug AND published = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;