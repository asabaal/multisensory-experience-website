// Supabase Client Configuration
// This file handles the connection to Supabase and provides blog-related functions

class SupabaseBlogClient {
    constructor() {
        // Initialize Supabase client
        // You'll need to replace these with your actual Supabase URL and anon key
        this.supabaseUrl = window.SUPABASE_URL || 'your-supabase-url';
        this.supabaseAnonKey = window.SUPABASE_ANON_KEY || 'your-supabase-anon-key';
        
        // Check if Supabase is available
        if (typeof supabase === 'undefined') {
            console.error('Supabase library not loaded. Please include the Supabase CDN script.');
            return;
        }
        
        this.client = supabase.createClient(this.supabaseUrl, this.supabaseAnonKey);
    }

    // Get all published blog posts with pagination
    async getBlogPosts(page = 1, limit = 10, featured = false) {
        try {
            let query = this.client
                .from('blog_posts_with_details')
                .select('*')
                .eq('published', true)
                .order('published_at', { ascending: false });

            if (featured) {
                query = query.eq('featured', true);
            }

            const from = (page - 1) * limit;
            const to = from + limit - 1;

            const { data, error, count } = await query
                .range(from, to);

            if (error) throw error;

            return {
                posts: data,
                totalCount: count,
                hasMore: count > (page * limit)
            };
        } catch (error) {
            console.error('Error fetching blog posts:', error);
            return { posts: [], totalCount: 0, hasMore: false };
        }
    }

    // Get a single blog post by slug with full content
    async getBlogPostBySlug(slug) {
        try {
            const { data, error } = await this.client
                .rpc('get_post_with_content', { post_slug: slug });

            if (error) throw error;

            // Increment view count
            await this.incrementViewCount(slug);

            return data;
        } catch (error) {
            console.error('Error fetching blog post:', error);
            return null;
        }
    }

    // Increment view count for a post
    async incrementViewCount(slug) {
        try {
            const { error } = await this.client
                .rpc('increment_post_views', { post_slug: slug });

            if (error) throw error;
        } catch (error) {
            console.error('Error incrementing view count:', error);
        }
    }

    // Get all tags
    async getTags() {
        try {
            const { data, error } = await this.client
                .from('tags')
                .select('*')
                .order('name');

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Error fetching tags:', error);
            return [];
        }
    }

    // Get posts by tag
    async getPostsByTag(tagSlug, page = 1, limit = 10) {
        try {
            const { data, error } = await this.client
                .from('blog_posts_with_details')
                .select('*')
                .eq('published', true)
                .contains('tags', `[{"slug": "${tagSlug}"}]`)
                .order('published_at', { ascending: false })
                .range((page - 1) * limit, page * limit - 1);

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Error fetching posts by tag:', error);
            return [];
        }
    }

    // Search posts
    async searchPosts(query, page = 1, limit = 10) {
        try {
            const { data, error } = await this.client
                .from('blog_posts_with_details')
                .select('*')
                .eq('published', true)
                .or(`title.ilike.%${query}%,excerpt.ilike.%${query}%`)
                .order('published_at', { ascending: false })
                .range((page - 1) * limit, page * limit - 1);

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Error searching posts:', error);
            return [];
        }
    }

    // Get recent posts (for sidebar, etc.)
    async getRecentPosts(limit = 5) {
        try {
            const { data, error } = await this.client
                .from('blog_posts_with_details')
                .select('id, title, slug, published_at, cover_image_url')
                .eq('published', true)
                .order('published_at', { ascending: false })
                .limit(limit);

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Error fetching recent posts:', error);
            return [];
        }
    }

    // Convert local blog data to Supabase format (migration helper)
    formatPostForSupabase(localPost) {
        return {
            title: localPost.title,
            slug: localPost.slug,
            excerpt: localPost.excerpt,
            cover_image_url: localPost.image,
            content: localPost.content || {},
            published: true,
            published_at: new Date(localPost.date).toISOString(),
            meta_title: localPost.title,
            meta_description: localPost.excerpt,
            reading_time_minutes: this.estimateReadingTime(localPost.excerpt)
        };
    }

    // Estimate reading time (helper function)
    estimateReadingTime(text) {
        const wordsPerMinute = 200;
        const wordCount = text.split(' ').length;
        return Math.ceil(wordCount / wordsPerMinute);
    }

    // Format date for display
    formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Generate post URL
    getPostUrl(slug) {
        return `blog/post-${slug}.html`;
    }
}

// Create global instance
window.supabaseBlog = new SupabaseBlogClient();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseBlogClient;
}