// Contact Forms & Email Subscriptions for Asabaal Ventures
// Simple integration with Supabase - no blog database needed!

class ContactAPI {
    constructor() {
        // Get your Supabase URL and key from environment or meta tags
        this.supabaseUrl = this.getConfig('VITE_SUPABASE_URL');
        this.supabaseKey = this.getConfig('VITE_SUPABASE_ANON_KEY');
        
        if (!this.supabaseUrl || !this.supabaseKey) {
            console.warn('Supabase not configured. Forms will not work until you add your credentials.');
            return;
        }
        
        this.client = supabase.createClient(this.supabaseUrl, this.supabaseKey);
        this.setupForms();
    }
    
    getConfig(name) {
        // Try window variables first (easiest for static sites)
        if (window[name]) return window[name];
        
        // Try meta tags
        const meta = document.querySelector(`meta[name="${name}"]`);
        if (meta) return meta.getAttribute('content');
        
        return null;
    }
    
    setupForms() {
        // Setup contact forms
        document.querySelectorAll('.contact-form, [data-form-type="contact"]').forEach(form => {
            form.addEventListener('submit', (e) => this.handleContact(e));
        });
        
        // Setup subscription forms
        document.querySelectorAll('.subscription-form, [data-form-type="subscription"]').forEach(form => {
            form.addEventListener('submit', (e) => this.handleSubscription(e));
        });
        
        // Setup unsubscribe forms
        document.querySelectorAll('.unsubscribe-form, [data-form-type="unsubscribe"]').forEach(form => {
            form.addEventListener('submit', (e) => this.handleUnsubscribe(e));
        });
        
        // Setup Discord signup forms
        document.querySelectorAll('.discord-signup-form, [data-form-type="discord"]').forEach(form => {
            form.addEventListener('submit', (e) => this.handleDiscordSignup(e));
        });
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    async handleContact(event) {
        event.preventDefault();
        const form = event.target;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        // Show loading
        button.disabled = true;
        button.textContent = 'Sending...';
        
        try {
            const formData = new FormData(form);
            
            const { error } = await this.client
                .from('contact_messages')
                .insert([{
                    name: formData.get('name'),
                    email: formData.get('email'),
                    subject: formData.get('subject') || null,
                    message: formData.get('message'),
                    source: formData.get('source') || 'website'
                }]);
            
            if (error) throw error;
            
            this.showMessage(form, 'Message sent successfully! We\'ll get back to you soon.', 'success');
            form.reset();
            
            // Send Discord notification
            this.sendDiscordNotification('contact', {
                name: formData.get('name'),
                email: formData.get('email'),
                subject: formData.get('subject') || '(No subject)',
                message: formData.get('message'),
                source: formData.get('source') || 'website'
            });
            
        } catch (error) {
            console.error('Contact form error:', error);
            this.showMessage(form, 'Failed to send message. Please try again.', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    async handleSubscription(event) {
        event.preventDefault();
        const form = event.target;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        // Show loading
        button.disabled = true;
        button.textContent = 'Subscribing...';
        
        try {
            const formData = new FormData(form);
            
            const { error } = await this.client
                .from('email_subscribers')
                .insert([{
                    email: formData.get('email'),
                    name: formData.get('name') || null,
                    subscription_source: formData.get('source') || 'website'
                }]);
            
            if (error) {
                if (error.message.includes('duplicate key')) {
                    throw new Error('This email is already subscribed!');
                }
                throw error;
            }
            
            this.showMessage(form, 'Successfully subscribed! Welcome to the community.', 'success');
            form.reset();
            
            // Send Discord notification
            this.sendDiscordNotification('subscribe', {
                email: formData.get('email'),
                name: formData.get('name') || '(No name provided)',
                source: formData.get('source') || 'website'
            });
            
        } catch (error) {
            console.error('Subscription error:', error);
            this.showMessage(form, error.message || 'Failed to subscribe. Please try again.', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    async handleUnsubscribe(event) {
        event.preventDefault();
        const form = event.target;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        // Show loading
        button.disabled = true;
        button.textContent = 'Unsubscribing...';
        
        try {
            const formData = new FormData(form);
            const email = formData.get('email');
            
            if (!email) {
                throw new Error('Please enter your email address');
            }
            
            const emailToSearch = email.toLowerCase().trim();
            console.log('Attempting to unsubscribe:', emailToSearch);
            
            // First check if the email exists
            const { data: existingRecord, error: selectError } = await this.client
                .from('email_subscribers')
                .select('*')
                .eq('email', emailToSearch);
                
            console.log('Found records:', existingRecord);
            
            if (selectError) {
                console.error('Error searching for email:', selectError);
                throw selectError;
            }
            
            if (!existingRecord || existingRecord.length === 0) {
                throw new Error(`Email "${emailToSearch}" not found in our subscriber list. Make sure you entered the exact email you subscribed with.`);
            }
            
            // Now update it
            const { data, error } = await this.client
                .from('email_subscribers')
                .update({
                    status: 'unsubscribed',
                    unsubscribed_at: new Date().toISOString()
                })
                .eq('email', emailToSearch)
                .select();
            
            console.log('Update result:', { data, error });
            
            if (error) {
                throw error;
            }
            
            if (!data || data.length === 0) {
                throw new Error('Email not found in our subscriber list');
            }
            
            this.showMessage(form, 'Successfully unsubscribed from our newsletter.', 'success');
            form.reset();
            
        } catch (error) {
            console.error('Unsubscribe error:', error);
            this.showMessage(form, error.message || 'Failed to unsubscribe. Please try again.', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    async handleDiscordSignup(event) {
        event.preventDefault();
        const form = event.target;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        // Show loading
        button.disabled = true;
        button.textContent = 'Joining Discord...';
        
        try {
            const formData = new FormData(form);
            const email = formData.get('email');
            const name = formData.get('name') || 'Discord Member';
            const discordUsername = formData.get('discord_username') || '';
            
            if (!discordUsername) {
                throw new Error('Please enter your Discord username');
            }
            
            // Validate email format only if email is provided
            if (email && !this.isValidEmail(email)) {
                throw new Error('Please enter a valid email address');
            }
            
            const cleanEmail = email ? email.toLowerCase().trim() : null;
            
            // Check if already signed up for Discord (by email if provided, otherwise by Discord username)
            let existingRecord = null;
            if (cleanEmail) {
                const { data } = await this.client
                    .from('email_subscribers')
                    .select('*')
                    .eq('email', cleanEmail)
                    .eq('discord_signup', true)
                    .single();
                existingRecord = data;
            } else {
                // Check by Discord username if no email provided
                const { data } = await this.client
                    .from('email_subscribers')
                    .select('*')
                    .eq('discord_username', discordUsername)
                    .eq('discord_signup', true)
                    .single();
                existingRecord = data;
            }
            
            if (existingRecord) {
                throw new Error('You\'re already signed up for our Discord community!');
            }
            
            // Insert/update subscriber record with Discord signup flag
            const recordData = {
                name: name,
                discord_username: discordUsername,
                discord_signup: true,
                subscribed_at: new Date().toISOString(),
                source: 'discord_signup'
            };
            
            // Only include email if provided
            if (cleanEmail) {
                recordData.email = cleanEmail;
            }
            
            const { error: insertError } = await this.client
                .from('email_subscribers')
                .upsert(recordData);
            
            if (insertError) throw insertError;
            
            // Send Discord notification
            await this.sendDiscordNotification('discord_signup', {
                name: name,
                email: cleanEmail || 'Not provided',
                discord_username: discordUsername
            });
            
            // Generate Discord invite link
            const discordInviteLink = window.DISCORD_INVITE_URL || 'https://discord.gg/YourInviteCode';
            
            // Show success message with clear next steps
            this.showMessage(form, 
                `✅ Success! Your Discord signup is complete.<br><br>
                <strong>Next Step:</strong> Click here to join the server: <br>
                <a href="${discordInviteLink}" target="_blank" style="color: #ffffff; text-decoration: underline; font-size: 1.1em; font-weight: bold; background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 6px; display: inline-block; margin-top: 8px;">🎮 Join Discord Server</a><br><br>
                <small>We've saved your Discord username (${discordUsername}) to help identify you in the server.</small>`, 
                'success'
            );
            
            form.reset();
            
            // Auto-open Discord invite after a short delay for better UX
            setTimeout(() => {
                window.open(discordInviteLink, '_blank');
            }, 1500);
            
        } catch (error) {
            console.error('Discord signup error:', error);
            this.showMessage(form, error.message || 'Failed to join Discord community. Please try again.', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    showMessage(form, message, type) {
        // Remove existing messages
        form.querySelectorAll('.form-message').forEach(msg => msg.remove());
        
        // Create new message
        const messageEl = document.createElement('div');
        messageEl.className = 'form-message';
        messageEl.innerHTML = message;
        messageEl.style.cssText = `
            margin-top: 15px;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: 500;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
        `;
        
        form.appendChild(messageEl);
        
        // Auto-remove success messages
        if (type === 'success') {
            setTimeout(() => messageEl.remove(), 5000);
        }
    }
    
    async sendDiscordNotification(type, data) {
        if (!window.DISCORD_WEBHOOK_URL) {
            console.log('Discord webhook not configured - skipping notification');
            return;
        }
        
        console.log('Sending Discord notification:', { type, data });
        
        try {
            let embed;
            
            if (type === 'contact') {
                embed = {
                    title: "📧 New Contact Form Submission",
                    color: 0x8b5cf6, // Purple color
                    fields: [
                        { name: "Name", value: data.name, inline: true },
                        { name: "Email", value: data.email, inline: true },
                        { name: "Subject", value: data.subject, inline: false },
                        { name: "Message", value: data.message.length > 1000 ? data.message.substring(0, 1000) + "..." : data.message, inline: false },
                        { name: "Source", value: data.source, inline: true }
                    ],
                    timestamp: new Date().toISOString(),
                    footer: { text: "Asabaal Ventures Website" }
                };
            } else if (type === 'subscribe') {
                embed = {
                    title: "📮 New Newsletter Subscription",
                    color: 0x10b981, // Green color
                    fields: [
                        { name: "Email", value: data.email, inline: true },
                        { name: "Name", value: data.name, inline: true },
                        { name: "Source", value: data.source, inline: true }
                    ],
                    timestamp: new Date().toISOString(),
                    footer: { text: "Asabaal Ventures Website" }
                };
            } else if (type === 'discord_signup') {
                embed = {
                    title: "🎮 New Discord Community Signup",
                    color: 0x5865f2, // Discord brand color
                    fields: [
                        { name: "Name", value: data.name, inline: true },
                        { name: "Email", value: data.email, inline: true },
                        { name: "Discord Username", value: data.discord_username || "Not provided", inline: true }
                    ],
                    timestamp: new Date().toISOString(),
                    footer: { text: "Asabaal Ventures Discord Community" }
                };
            }
            
            const response = await fetch(window.DISCORD_WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    embeds: [embed]
                })
            });
            
            if (response.ok) {
                console.log('✅ Discord notification sent successfully');
            } else {
                const errorText = await response.text();
                console.error('❌ Failed to send Discord notification:', {
                    status: response.status,
                    statusText: response.statusText,
                    error: errorText
                });
            }
        } catch (error) {
            console.error('Error sending Discord notification:', error);
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.contactAPI = new ContactAPI();
});