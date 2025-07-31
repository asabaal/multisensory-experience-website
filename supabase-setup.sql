-- Supabase Database Setup for Asabaal Ventures Website
-- Execute these SQL commands in your Supabase SQL Editor

-- =====================================================
-- TABLES SETUP
-- =====================================================

-- 1. Contact Messages Table
CREATE TABLE IF NOT EXISTS contact_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    source VARCHAR(100) DEFAULT 'website', -- Track where message came from
    status VARCHAR(50) DEFAULT 'unread', -- unread, read, replied, archived
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Email Subscribers Table
CREATE TABLE IF NOT EXISTS email_subscribers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    subscription_source VARCHAR(100) DEFAULT 'website', -- website, blog, contest, etc.
    status VARCHAR(50) DEFAULT 'active', -- active, unsubscribed, bounced
    preferences JSONB DEFAULT '{}', -- Store subscription preferences
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Email Campaigns Table (for future use)
CREATE TABLE IF NOT EXISTS email_campaigns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT,
    status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, sent
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    recipient_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Contact messages indexes
CREATE INDEX IF NOT EXISTS idx_contact_messages_created_at ON contact_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contact_messages_status ON contact_messages(status);
CREATE INDEX IF NOT EXISTS idx_contact_messages_email ON contact_messages(email);

-- Email subscribers indexes
CREATE INDEX IF NOT EXISTS idx_email_subscribers_email ON email_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_email_subscribers_status ON email_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_email_subscribers_subscribed_at ON email_subscribers(subscribed_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_campaigns ENABLE ROW LEVEL SECURITY;

-- Contact Messages Policies
-- Allow anonymous users to insert messages (for contact form)
CREATE POLICY "Allow anonymous message submission" 
ON contact_messages FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow authenticated users (you) to read all messages
CREATE POLICY "Allow authenticated read access to messages" 
ON contact_messages FOR SELECT 
TO authenticated 
USING (true);

-- Allow authenticated users to update message status
CREATE POLICY "Allow authenticated update to messages" 
ON contact_messages FOR UPDATE 
TO authenticated 
USING (true);

-- Email Subscribers Policies
-- Allow anonymous users to subscribe
CREATE POLICY "Allow anonymous email subscription" 
ON email_subscribers FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow users to unsubscribe using their email
CREATE POLICY "Allow email unsubscription" 
ON email_subscribers FOR UPDATE 
TO anon 
USING (true)
WITH CHECK (true);

-- Allow authenticated users (you) to read all subscribers
CREATE POLICY "Allow authenticated read access to subscribers" 
ON email_subscribers FOR SELECT 
TO authenticated 
USING (true);

-- Email Campaigns Policies (admin only)
CREATE POLICY "Allow authenticated access to campaigns" 
ON email_campaigns FOR ALL 
TO authenticated 
USING (true);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to automatically update 'updated_at'
CREATE TRIGGER update_contact_messages_updated_at
    BEFORE UPDATE ON contact_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_email_subscribers_updated_at
    BEFORE UPDATE ON email_subscribers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_email_campaigns_updated_at
    BEFORE UPDATE ON email_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Function to prevent duplicate email subscriptions
CREATE OR REPLACE FUNCTION prevent_duplicate_subscription()
RETURNS TRIGGER AS $$
BEGIN
    -- If email already exists and is active, prevent insertion
    IF EXISTS (
        SELECT 1 FROM email_subscribers 
        WHERE email = NEW.email AND status = 'active'
    ) THEN
        RAISE EXCEPTION 'Email already subscribed';
    END IF;
    
    -- If email exists but is unsubscribed, reactivate it
    IF EXISTS (
        SELECT 1 FROM email_subscribers 
        WHERE email = NEW.email AND status = 'unsubscribed'
    ) THEN
        UPDATE email_subscribers 
        SET 
            status = 'active',
            name = COALESCE(NEW.name, name),
            subscription_source = NEW.subscription_source,
            subscribed_at = NOW(),
            unsubscribed_at = NULL,
            updated_at = NOW()
        WHERE email = NEW.email;
        RETURN NULL; -- Prevent the INSERT
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to prevent duplicate subscriptions
CREATE TRIGGER prevent_duplicate_email_subscription
    BEFORE INSERT ON email_subscribers
    FOR EACH ROW
    EXECUTE FUNCTION prevent_duplicate_subscription();

-- =====================================================
-- USEFUL VIEWS FOR ANALYTICS
-- =====================================================

-- View for unread messages count
CREATE OR REPLACE VIEW unread_messages_count AS
SELECT COUNT(*) as count
FROM contact_messages
WHERE status = 'unread';

-- View for active subscribers count
CREATE OR REPLACE VIEW active_subscribers_count AS
SELECT COUNT(*) as count
FROM email_subscribers
WHERE status = 'active';

-- View for daily message stats
CREATE OR REPLACE VIEW daily_message_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as message_count,
    COUNT(CASE WHEN status = 'unread' THEN 1 END) as unread_count
FROM contact_messages
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- View for subscription growth
CREATE OR REPLACE VIEW subscription_growth AS
SELECT 
    DATE(subscribed_at) as date,
    COUNT(*) as new_subscribers,
    SUM(COUNT(*)) OVER (ORDER BY DATE(subscribed_at)) as total_subscribers
FROM email_subscribers
WHERE status = 'active'
GROUP BY DATE(subscribed_at)
ORDER BY date DESC;

-- =====================================================
-- INITIAL DATA (OPTIONAL)
-- =====================================================

-- You can insert some test data if needed
-- INSERT INTO contact_messages (name, email, subject, message) 
-- VALUES ('Test User', 'test@example.com', 'Test Subject', 'Test message content');