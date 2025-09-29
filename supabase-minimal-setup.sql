-- Minimal Supabase Setup for Asabaal Ventures
-- Only includes contact forms and email subscriptions (no blog database needed!)

-- =====================================================
-- CONTACT MESSAGES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS contact_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    source VARCHAR(100) DEFAULT 'website',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- EMAIL SUBSCRIBERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS email_subscribers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    subscription_source VARCHAR(100) DEFAULT 'website',
    status VARCHAR(50) DEFAULT 'active',
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    unsubscribed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_subscribers ENABLE ROW LEVEL SECURITY;

-- Allow anyone to submit contact forms
CREATE POLICY "Anyone can submit contact messages" 
ON contact_messages FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow anyone to subscribe
CREATE POLICY "Anyone can subscribe" 
ON email_subscribers FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow email owners to unsubscribe themselves
CREATE POLICY "Users can unsubscribe themselves" 
ON email_subscribers FOR UPDATE 
TO anon 
USING (true)
WITH CHECK (true);

-- That's it! Simple and ready to deploy.