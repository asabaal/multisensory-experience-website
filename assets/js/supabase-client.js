// Supabase Client Configuration for Asabaal Ventures Website
// This file handles all backend API interactions including blog, contact, and subscriptions

class SupabaseClient {
    constructor() {
        // Get environment variables
        this.supabaseUrl = this.getEnvVar('VITE_SUPABASE_URL') || window.SUPABASE_URL || 'your-supabase-url';
        this.supabaseAnonKey = this.getEnvVar('VITE_SUPABASE_ANON_KEY') || window.SUPABASE_ANON_KEY || 'your-supabase-anon-key';
        
        // Validate configuration
        if (!this.supabaseUrl || !this.supabaseAnonKey || 
            this.supabaseUrl === 'your-supabase-url' || 
            this.supabaseAnonKey === 'your-supabase-anon-key') {
            console.error('Supabase configuration missing. Please check your environment variables.');
            return;
        }
        
        // Check if Supabase is available
        if (typeof supabase === 'undefined') {
            console.error('Supabase library not loaded. Please include the Supabase CDN script.');
            return;
        }
        
        this.client = supabase.createClient(this.supabaseUrl, this.supabaseAnonKey);
        
        // API endpoints for direct REST calls
        this.endpoints = {
            messages: `${this.supabaseUrl}/rest/v1/contact_messages`,
            subscribers: `${this.supabaseUrl}/rest/v1/email_subscribers`,
            unreadCount: `${this.supabaseUrl}/rest/v1/unread_messages_count`,
            subscriberCount: `${this.supabaseUrl}/rest/v1/active_subscribers_count`
        };
        
        // Common headers
        this.headers = {
            'apikey': this.supabaseAnonKey,
            'Authorization': `Bearer ${this.supabaseAnonKey}`,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        };
    }
    
    // Get environment variable with fallback options
    getEnvVar(name) {
        // First try process.env (if using build tools)
        if (typeof process !== 'undefined' && process.env && process.env[name]) {
            return process.env[name];
        }
        
        // Then try window (if set globally)
        if (typeof window !== 'undefined' && window[name]) {
            return window[name];
        }
        
        // Finally try meta tags
        const meta = document.querySelector(`meta[name="${name}"]`);
        if (meta) {
            return meta.getAttribute('content');
        }
        
        return null;
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
    
    // =====================================================
    // CONTACT MESSAGES API
    // =====================================================
    
    /**
     * Submit a contact form message
     * @param {Object} messageData - The message data
     * @param {string} messageData.name - Sender's name
     * @param {string} messageData.email - Sender's email
     * @param {string} messageData.subject - Message subject (optional)
     * @param {string} messageData.message - Message content
     * @param {string} messageData.source - Source of message (default: 'website')
     * @returns {Promise<Object>} Response object
     */
    async submitContactMessage(messageData) {
        try {
            // Validate required fields
            const required = ['name', 'email', 'message'];
            for (const field of required) {
                if (!messageData[field] || messageData[field].trim() === '') {
                    throw new Error(`${field} is required`);
                }
            }
            
            // Validate email format
            if (!this.isValidEmail(messageData.email)) {
                throw new Error('Please enter a valid email address');
            }
            
            // Use Supabase client for insertion
            const { data, error } = await this.client
                .from('contact_messages')
                .insert([{
                    name: messageData.name.trim(),
                    email: messageData.email.trim().toLowerCase(),
                    subject: messageData.subject ? messageData.subject.trim() : null,
                    message: messageData.message.trim(),
                    source: messageData.source || 'website'
                }]);
            
            if (error) {
                throw new Error(error.message);
            }
            
            return {
                success: true,
                message: 'Message sent successfully! We\'ll get back to you soon.'
            };
            
        } catch (error) {
            console.error('Error submitting contact message:', error);
            return {
                success: false,
                message: error.message || 'Failed to send message. Please try again.'
            };
        }
    }
    
    // =====================================================
    // EMAIL SUBSCRIPTION API
    // =====================================================
    
    /**
     * Subscribe an email to the mailing list
     * @param {Object} subscriptionData - The subscription data
     * @param {string} subscriptionData.email - Subscriber's email
     * @param {string} subscriptionData.name - Subscriber's name (optional)
     * @param {string} subscriptionData.source - Source of subscription (default: 'website')
     * @returns {Promise<Object>} Response object
     */
    async subscribeEmail(subscriptionData) {
        try {
            // Validate email
            if (!subscriptionData.email || !this.isValidEmail(subscriptionData.email)) {
                throw new Error('Please enter a valid email address');
            }
            
            // Use Supabase client for insertion
            const { data, error } = await this.client
                .from('email_subscribers')
                .insert([{
                    email: subscriptionData.email.trim().toLowerCase(),
                    name: subscriptionData.name ? subscriptionData.name.trim() : null,
                    subscription_source: subscriptionData.source || 'website'
                }]);
            
            if (error) {
                // Handle duplicate subscription
                if (error.message.includes('Email already subscribed') || 
                    error.message.includes('duplicate key')) {
                    return {
                        success: false,
                        message: 'This email is already subscribed to our newsletter.'
                    };
                }
                throw new Error(error.message);
            }
            
            return {
                success: true,
                message: 'Successfully subscribed! Welcome to the Asabaal Ventures community.'
            };
            
        } catch (error) {
            console.error('Error subscribing email:', error);
            return {
                success: false,
                message: error.message || 'Failed to subscribe. Please try again.'
            };
        }
    }
    
    /**
     * Unsubscribe an email from the mailing list
     * @param {string} email - Email to unsubscribe
     * @returns {Promise<Object>} Response object
     */
    async unsubscribeEmail(email) {
        try {
            if (!email || !this.isValidEmail(email)) {
                throw new Error('Please enter a valid email address');
            }
            
            const { data, error } = await this.client
                .from('email_subscribers')
                .update({
                    status: 'unsubscribed',
                    unsubscribed_at: new Date().toISOString()
                })
                .eq('email', email.trim().toLowerCase());
            
            if (error) {
                throw new Error(error.message);
            }
            
            return {
                success: true,
                message: 'Successfully unsubscribed from our newsletter.'
            };
            
        } catch (error) {
            console.error('Error unsubscribing email:', error);
            return {
                success: false,
                message: error.message || 'Failed to unsubscribe. Please try again.'
            };
        }
    }
    
    // =====================================================
    // UTILITY METHODS
    // =====================================================
    
    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} Whether email is valid
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    /**
     * Get analytics data (for admin use)
     * @returns {Promise<Object>} Analytics data
     */
    async getAnalytics() {
        try {
            // Use Supabase views for analytics
            const [unreadResult, subscriberResult] = await Promise.all([
                this.client.from('unread_messages_count').select('count').single(),
                this.client.from('active_subscribers_count').select('count').single()
            ]);
            
            return {
                unreadMessages: unreadResult.data?.count || 0,
                activeSubscribers: subscriberResult.data?.count || 0
            };
            
        } catch (error) {
            console.error('Error fetching analytics:', error);
            return {
                unreadMessages: 0,
                activeSubscribers: 0
            };
        }
    }
}

// Create global instance
window.SupabaseAPI = new SupabaseClient();
// Maintain backward compatibility
window.supabaseBlog = window.SupabaseAPI;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseClient;
}