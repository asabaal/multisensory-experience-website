// Supabase Configuration
// This file manages environment variables and configuration for Supabase

// Development/Production Configuration
const SupabaseConfig = {
    // Replace these with your actual Supabase project details
    url: 'https://your-project-id.supabase.co',
    anonKey: 'your-anon-key-here',
    
    // API endpoints
    apiUrl: function() {
        return `${this.url}/rest/v1`;
    },
    
    // Storage configuration
    storage: {
        bucketName: 'blog-assets',
        publicUrl: function(path) {
            return `${SupabaseConfig.url}/storage/v1/object/public/${this.bucketName}/${path}`;
        }
    },
    
    // Database table names
    tables: {
        blogPosts: 'blog_posts',
        tags: 'tags',
        authors: 'authors',
        blogPostTags: 'blog_post_tags',
        contentSections: 'content_sections'
    },
    
    // Views and functions
    views: {
        blogPostsWithDetails: 'blog_posts_with_details'
    },
    
    functions: {
        getPostWithContent: 'get_post_with_content',
        incrementPostViews: 'increment_post_views'
    }
};

// Environment-specific overrides
if (window.location.hostname === 'localhost') {
    // Development settings
    console.log('Using development Supabase configuration');
} else {
    // Production settings
    console.log('Using production Supabase configuration');
}

// Make config available globally
window.SUPABASE_CONFIG = SupabaseConfig;

// Also make individual values available for backward compatibility
window.SUPABASE_URL = SupabaseConfig.url;
window.SUPABASE_ANON_KEY = SupabaseConfig.anonKey;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseConfig;
}