// Form handling for Asabaal Ventures Website
// Handles contact forms and email subscriptions

class FormHandler {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupForms();
            });
        } else {
            this.setupForms();
        }
    }

    setupForms() {
        // Setup contact forms
        this.setupContactForms();
        
        // Setup email subscription forms
        this.setupSubscriptionForms();
        
        // Setup unsubscribe forms (if any)
        this.setupUnsubscribeForms();
    }

    // =====================================================
    // CONTACT FORM HANDLING
    // =====================================================

    setupContactForms() {
        const contactForms = document.querySelectorAll('.contact-form, #contact-form, [data-form-type="contact"]');
        
        contactForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleContactSubmit(e));
        });
    }

    async handleContactSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        const originalButtonText = submitButton ? submitButton.textContent : '';
        
        // Show loading state
        this.setFormLoading(form, submitButton, true);
        
        try {
            // Get form data
            const formData = new FormData(form);
            const messageData = {
                name: formData.get('name')?.trim(),
                email: formData.get('email')?.trim(),
                subject: formData.get('subject')?.trim(),
                message: formData.get('message')?.trim(),
                source: formData.get('source') || 'website'
            };
            
            // Basic validation
            if (!messageData.name || !messageData.email || !messageData.message) {
                throw new Error('Please fill in all required fields');
            }
            
            // Submit to Supabase
            const result = await window.SupabaseAPI.submitContactMessage(messageData);
            
            if (result.success) {
                this.showFormMessage(form, result.message, 'success');
                form.reset();
                
                // Track success event (if analytics available)
                this.trackEvent('contact_form_submit', {
                    source: messageData.source,
                    has_subject: !!messageData.subject
                });
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Contact form error:', error);
            this.showFormMessage(form, error.message || 'Failed to send message. Please try again.', 'error');
            
            // Track error event
            this.trackEvent('contact_form_error', {
                error: error.message
            });
        } finally {
            // Reset loading state
            this.setFormLoading(form, submitButton, false, originalButtonText);
        }
    }

    // =====================================================
    // EMAIL SUBSCRIPTION HANDLING
    // =====================================================

    setupSubscriptionForms() {
        const subscriptionForms = document.querySelectorAll('.subscription-form, #email-subscription, [data-form-type="subscription"]');
        
        subscriptionForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleSubscriptionSubmit(e));
        });
    }

    async handleSubscriptionSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        const originalButtonText = submitButton ? submitButton.textContent : '';
        
        // Show loading state
        this.setFormLoading(form, submitButton, true);
        
        try {
            // Get form data
            const formData = new FormData(form);
            const subscriptionData = {
                email: formData.get('email')?.trim(),
                name: formData.get('name')?.trim(),
                source: formData.get('source') || 'website'
            };
            
            // Basic validation
            if (!subscriptionData.email) {
                throw new Error('Please enter your email address');
            }
            
            // Submit to Supabase
            const result = await window.SupabaseAPI.subscribeEmail(subscriptionData);
            
            if (result.success) {
                this.showFormMessage(form, result.message, 'success');
                form.reset();
                
                // Track success event
                this.trackEvent('email_subscription', {
                    source: subscriptionData.source,
                    has_name: !!subscriptionData.name
                });
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Subscription form error:', error);
            this.showFormMessage(form, error.message || 'Failed to subscribe. Please try again.', 'error');
            
            // Track error event
            this.trackEvent('email_subscription_error', {
                error: error.message
            });
        } finally {
            // Reset loading state
            this.setFormLoading(form, submitButton, false, originalButtonText);
        }
    }

    // =====================================================
    // UNSUBSCRIBE HANDLING
    // =====================================================

    setupUnsubscribeForms() {
        const unsubscribeForms = document.querySelectorAll('.unsubscribe-form, #unsubscribe-form, [data-form-type="unsubscribe"]');
        
        unsubscribeForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleUnsubscribeSubmit(e));
        });
    }

    async handleUnsubscribeSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        const originalButtonText = submitButton ? submitButton.textContent : '';
        
        // Show loading state
        this.setFormLoading(form, submitButton, true);
        
        try {
            // Get form data
            const formData = new FormData(form);
            const email = formData.get('email')?.trim();
            
            // Basic validation
            if (!email) {
                throw new Error('Please enter your email address');
            }
            
            // Submit to Supabase
            const result = await window.SupabaseAPI.unsubscribeEmail(email);
            
            if (result.success) {
                this.showFormMessage(form, result.message, 'success');
                form.reset();
                
                // Track success event
                this.trackEvent('email_unsubscribe', {
                    source: 'website'
                });
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Unsubscribe form error:', error);
            this.showFormMessage(form, error.message || 'Failed to unsubscribe. Please try again.', 'error');
            
            // Track error event
            this.trackEvent('email_unsubscribe_error', {
                error: error.message
            });
        } finally {
            // Reset loading state
            this.setFormLoading(form, submitButton, false, originalButtonText);
        }
    }

    // =====================================================
    // UTILITY METHODS
    // =====================================================

    setFormLoading(form, submitButton, isLoading, originalText = '') {
        if (submitButton) {
            if (isLoading) {
                submitButton.disabled = true;
                submitButton.textContent = 'Sending...';
                submitButton.classList.add('loading');
            } else {
                submitButton.disabled = false;
                submitButton.textContent = originalText || 'Send';
                submitButton.classList.remove('loading');
            }
        }
        
        // Add/remove loading class to form
        if (isLoading) {
            form.classList.add('loading');
        } else {
            form.classList.remove('loading');
        }
    }

    showFormMessage(form, message, type = 'info') {
        // Remove any existing messages
        const existingMessages = form.querySelectorAll('.form-message');
        existingMessages.forEach(msg => msg.remove());
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `form-message form-message--${type}`;
        messageEl.textContent = message;
        
        // Style the message
        Object.assign(messageEl.style, {
            padding: '12px 16px',
            borderRadius: '8px',
            marginTop: '16px',
            fontSize: '14px',
            fontWeight: '500',
            backgroundColor: type === 'success' ? '#10b981' : 
                          type === 'error' ? '#ef4444' : '#6b7280',
            color: '#ffffff',
            border: 'none',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        });
        
        // Insert message after form
        form.appendChild(messageEl);
        
        // Auto-remove success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.remove();
                }
            }, 5000);
        }
        
        // Scroll message into view
        messageEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    trackEvent(eventName, data = {}) {
        // Track events with Google Analytics if available
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, data);
        }
        
        // Track with other analytics services if available
        if (typeof analytics !== 'undefined') {
            analytics.track(eventName, data);
        }
        
        // Console log for debugging
        console.log(`Event: ${eventName}`, data);
    }

    // =====================================================
    // QUICK SUBSCRIPTION INTEGRATION
    // =====================================================

    /**
     * Add a quick subscription form to any element
     * @param {string} selector - CSS selector for the container
     * @param {Object} options - Configuration options
     */
    addQuickSubscription(selector, options = {}) {
        const container = document.querySelector(selector);
        if (!container) return;
        
        const config = {
            placeholder: 'Enter your email...',
            buttonText: 'Subscribe',
            source: 'quick-form',
            showName: false,
            ...options
        };
        
        const formHTML = `
            <form class="quick-subscription-form subscription-form" data-form-type="subscription">
                <input type="hidden" name="source" value="${config.source}">
                ${config.showName ? '<input type="text" name="name" placeholder="Your name (optional)" style="margin-bottom: 8px;">' : ''}
                <div style="display: flex; gap: 8px; align-items: center;">
                    <input type="email" name="email" placeholder="${config.placeholder}" required 
                           style="flex: 1; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px;">
                    <button type="submit" style="padding: 8px 16px; background: #8b5cf6; color: white; border: none; border-radius: 6px; cursor: pointer;">
                        ${config.buttonText}
                    </button>
                </div>
            </form>
        `;
        
        container.innerHTML = formHTML;
        
        // Setup the new form
        this.setupSubscriptionForms();
    }
}

// Initialize form handler when script loads
const formHandler = new FormHandler();

// Make it globally available
window.FormHandler = FormHandler;
window.formHandler = formHandler;