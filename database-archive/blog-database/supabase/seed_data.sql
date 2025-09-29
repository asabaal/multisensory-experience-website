-- Seed Data for Blog
-- Run this to populate initial data from your existing blog posts

-- Insert default author (Asabaal Horan)
INSERT INTO authors (id, name, email, bio, avatar_url, website_url, social_links) 
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Asabaal Horan',
    'asabaal@asabaalventures.me',
    'Data Scientist | Entrepreneur | Educator. Co-Founder & Creative Visionary at Asabaal Ventures, building AI-native infrastructure for human flourishing in the post-scarcity economy.',
    '../assets/images/profiles/in-love-and-unity.png',
    'https://asabaalventures.me',
    '{"linkedin": "https://www.linkedin.com/in/asabaal-horan-phd-2144b689/"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- Insert initial tags
INSERT INTO tags (name, slug, description, color) VALUES
    ('Creativity', 'creativity', 'Posts about creative expression and innovation', '#f472b6'),
    ('AI', 'ai', 'Artificial Intelligence and its impact on humanity', '#8b5cf6'),
    ('Personal Journey', 'personal-journey', 'Personal reflections and growth stories', '#06b6d4'),
    ('Future', 'future', 'Visions and possibilities for tomorrow', '#10b981'),
    ('Vision 2054', 'vision-2054', 'The Great Reconciliation and unity consciousness', '#fbbf24'),
    ('Unity', 'unity', 'Building bridges and fostering connection', '#f59e0b'),
    ('Purpose', 'purpose', 'Finding and living your calling', '#ef4444'),
    ('Economics', 'economics', 'New economic models and systems', '#06b6d4'),
    ('Collaboration', 'collaboration', 'Working together for greater impact', '#10b981'),
    ('Innovation', 'innovation', 'Breakthrough ideas and approaches', '#8b5cf6')
ON CONFLICT (slug) DO NOTHING;

-- Insert the first blog post (Embracing the Age of Creativity)
INSERT INTO blog_posts (
    id,
    title, 
    slug, 
    excerpt, 
    cover_image_url, 
    content, 
    published, 
    featured,
    published_at,
    author_id,
    meta_title,
    meta_description,
    reading_time_minutes
) VALUES (
    '550e8400-e29b-41d4-a716-446655440001',
    'Embracing the Age of Creativity',
    'embracing-the-age-of-creativity',
    'A personal journey through transformation, embracing AI, and discovering peace amidst life''s challenges. Welcome to a new era where creativity and technology unite to shape our future.',
    '../assets/images/blog/20250512-cover-image.jpg',
    '{
        "subtitle": "A personal journey through transformation, embracing AI, and discovering peace amidst life''s challenges. Welcome to a new era where creativity and technology unite to shape our future.",
        "intro": "Hello, World! I find myself in a challenging season of life - recently fired from my job, selling one of my homes, going through a divorce, and living far from my family. It''s a time filled with anxiety and uncertainty, but amidst the chaos, I''ve discovered a profound sense of peace within myself.",
        "sections": [
            {
                "title": "The Transformation Moment",
                "content": [
                    "I''ve long yearned to share my talents and passions with the world, but I always felt limited by circumstance and opportunity. However, in 2023, everything changed, not just for me, but for the entire world.",
                    "As a highly educated individual and a practicing Data Scientist, I have witnessed the extraordinary power of AI come to life. This transformative technology has reshaped our understanding of what is possible, and in this pivotal moment, I realized something crucial - this is my time."
                ]
            }
        ],
        "quotes": [
            {
                "text": "The Age of Creativity is upon us, and I choose to embrace it wholeheartedly.",
                "author": ""
            },
            {
                "text": "Welcome to the Age of Creativity. Let''s make it beautiful.",
                "author": ""
            }
        ]
    }'::jsonb,
    true,
    true,
    '2024-05-12T00:00:00Z',
    '550e8400-e29b-41d4-a716-446655440000',
    'Embracing the Age of Creativity | Asabaal Ventures Blog',
    'A personal journey through transformation, embracing AI, and discovering peace amidst life''s challenges. Welcome to a new era where creativity and technology unite to shape our future.',
    5
) ON CONFLICT (slug) DO NOTHING;

-- Link the post to its tags
INSERT INTO blog_post_tags (post_id, tag_id)
SELECT 
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    t.id
FROM tags t 
WHERE t.slug IN ('creativity', 'ai', 'personal-journey', 'future')
ON CONFLICT (post_id, tag_id) DO NOTHING;

-- Insert content sections for the first post
INSERT INTO content_sections (post_id, section_type, title, content, order_index) VALUES
(
    '550e8400-e29b-41d4-a716-446655440001',
    'text',
    'The Transformation Moment',
    '{
        "paragraphs": [
            "I''ve long yearned to share my talents and passions with the world, but I always felt limited by circumstance and opportunity. However, in 2023, everything changed, not just for me, but for the entire world.",
            "As a highly educated individual and a practicing Data Scientist, I have witnessed the extraordinary power of AI come to life. This transformative technology has reshaped our understanding of what is possible, and in this pivotal moment, I realized something crucial - this is my time."
        ]
    }'::jsonb,
    1
),
(
    '550e8400-e29b-41d4-a716-446655440001',
    'quote',
    null,
    '{
        "text": "The Age of Creativity is upon us, and I choose to embrace it wholeheartedly.",
        "author": ""
    }'::jsonb,
    2
),
(
    '550e8400-e29b-41d4-a716-446655440001',
    'text',
    'A New Beginning',
    '{
        "paragraphs": [
            "You may love it or hate it, but I will love you regardless. I have made a conscious decision to let go of judgment and instead focus on the incredible potential that lies ahead. We stand at a threshold in human history, where we have the chance to create a beautiful future characterized by peace, passion, and the fulfillment of our deepest needs.",
            "In this blog, I invite you to join me on a personal journey of exploration and growth. Together, we will navigate the challenges and opportunities of this new era, delving into the ways in which creativity, technology, and human connection can transform our lives."
        ]
    }'::jsonb,
    3
);