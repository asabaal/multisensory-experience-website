-- Supabase Community Migration for Asabaal Ventures Discord Integration
-- This replaces the email_subscribers table with a community_members system

-- =====================================================
-- BACKUP AND DROP OLD TABLE
-- =====================================================

-- First, backup existing email subscribers if any exist
CREATE TABLE IF NOT EXISTS email_subscribers_backup AS 
SELECT * FROM email_subscribers;

-- Drop the old email_subscribers table
DROP TABLE IF EXISTS email_subscribers;

-- =====================================================
-- NEW COMMUNITY MEMBERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS community_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    discord_username VARCHAR(255),
    discord_id VARCHAR(255),
    discord_invite_code VARCHAR(255),
    
    -- Tracking fields
    invite_source VARCHAR(100) DEFAULT 'website', -- contact_form, newsletter, direct, etc.
    status VARCHAR(50) DEFAULT 'invited', -- invited, joined, active, inactive, banned
    
    -- Timestamps
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    joined_discord_at TIMESTAMP WITH TIME ZONE,
    last_active_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    join_ip VARCHAR(45), -- For basic analytics/security
    referrer VARCHAR(500), -- What page they came from
    user_agent TEXT, -- Browser info for analytics
    
    -- Preferences
    preferences JSONB DEFAULT '{}', -- Store notification preferences, interests, etc.
    
    -- Standard fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(email),
    UNIQUE(discord_id)
);

-- =====================================================
-- CONTACT MESSAGES TABLE (Keep existing, add fields)
-- =====================================================

-- Add community invitation tracking to contact messages
ALTER TABLE contact_messages ADD COLUMN IF NOT EXISTS 
    community_invite_sent BOOLEAN DEFAULT false;

ALTER TABLE contact_messages ADD COLUMN IF NOT EXISTS 
    community_member_id UUID REFERENCES community_members(id);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_community_members_email ON community_members(email);
CREATE INDEX IF NOT EXISTS idx_community_members_discord_id ON community_members(discord_id);
CREATE INDEX IF NOT EXISTS idx_community_members_status ON community_members(status);
CREATE INDEX IF NOT EXISTS idx_community_members_invited_at ON community_members(invited_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_members_source ON community_members(invite_source);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

ALTER TABLE community_members ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to join the community (register)
CREATE POLICY "Anyone can join community" 
ON community_members FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow anonymous users to read basic info (for Discord integration)
CREATE POLICY "Allow anonymous to read for Discord integration" 
ON community_members FOR SELECT 
TO anon 
USING (true);

-- Allow updates for Discord integration (when someone joins Discord)
CREATE POLICY "Allow community member updates" 
ON community_members FOR UPDATE 
TO anon 
USING (true)
WITH CHECK (true);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_community_member_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update 'updated_at'
CREATE TRIGGER update_community_members_updated_at
    BEFORE UPDATE ON community_members
    FOR EACH ROW
    EXECUTE FUNCTION update_community_member_updated_at();

-- Function to generate unique invite codes
CREATE OR REPLACE FUNCTION generate_invite_code()
RETURNS TEXT AS $$
BEGIN
    RETURN encode(gen_random_bytes(6), 'base64');
END;
$$ LANGUAGE plpgsql;

-- Function to create community member from contact form
CREATE OR REPLACE FUNCTION create_community_member_from_contact(
    p_email TEXT,
    p_name TEXT DEFAULT NULL,
    p_source TEXT DEFAULT 'contact_form'
)
RETURNS UUID AS $$
DECLARE
    member_id UUID;
BEGIN
    INSERT INTO community_members (
        email, 
        name, 
        invite_source,
        discord_invite_code
    ) VALUES (
        LOWER(TRIM(p_email)),
        p_name,
        p_source,
        generate_invite_code()
    ) 
    ON CONFLICT (email) DO UPDATE SET
        name = COALESCE(EXCLUDED.name, community_members.name),
        invite_source = EXCLUDED.invite_source,
        updated_at = NOW()
    RETURNING id INTO member_id;
    
    RETURN member_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- USEFUL VIEWS FOR ANALYTICS
-- =====================================================

-- View for active community stats
CREATE OR REPLACE VIEW community_stats AS
SELECT 
    COUNT(*) as total_members,
    COUNT(CASE WHEN status = 'joined' THEN 1 END) as joined_members,
    COUNT(CASE WHEN status = 'invited' THEN 1 END) as pending_invites,
    COUNT(CASE WHEN discord_id IS NOT NULL THEN 1 END) as discord_connected,
    COUNT(CASE WHEN invited_at >= NOW() - INTERVAL '7 days' THEN 1 END) as new_this_week,
    COUNT(CASE WHEN joined_discord_at >= NOW() - INTERVAL '7 days' THEN 1 END) as joined_this_week
FROM community_members;

-- View for invite source breakdown
CREATE OR REPLACE VIEW invite_source_stats AS
SELECT 
    invite_source,
    COUNT(*) as total_invites,
    COUNT(CASE WHEN status = 'joined' THEN 1 END) as successful_joins,
    ROUND(
        COUNT(CASE WHEN status = 'joined' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as conversion_rate
FROM community_members
GROUP BY invite_source
ORDER BY total_invites DESC;

-- View for recent activity
CREATE OR REPLACE VIEW recent_community_activity AS
SELECT 
    id,
    email,
    name,
    discord_username,
    status,
    invite_source,
    invited_at,
    joined_discord_at
FROM community_members
ORDER BY COALESCE(joined_discord_at, invited_at) DESC
LIMIT 50;

-- =====================================================
-- MIGRATE EXISTING DATA (if any)
-- =====================================================

-- Migrate any existing email subscribers to community members
INSERT INTO community_members (email, name, invite_source, status, invited_at)
SELECT 
    email,
    name,
    COALESCE(subscription_source, 'legacy_email') as invite_source,
    CASE 
        WHEN status = 'active' THEN 'invited'
        WHEN status = 'unsubscribed' THEN 'inactive'
        ELSE 'invited'
    END as status,
    COALESCE(subscribed_at, NOW()) as invited_at
FROM email_subscribers_backup
WHERE email IS NOT NULL
ON CONFLICT (email) DO NOTHING;

-- Clean up backup table (optional - remove if you want to keep it)
-- DROP TABLE email_subscribers_backup;

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================

-- Uncomment to add sample data for testing
-- INSERT INTO community_members (email, name, invite_source) VALUES
-- ('test@example.com', 'Test User', 'website_test'),
-- ('demo@asabaalventures.com', 'Demo User', 'direct_invite');

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

-- This will show in the Supabase SQL editor when migration completes
DO $$
BEGIN
    RAISE NOTICE 'Community migration completed successfully!';
    RAISE NOTICE 'New table: community_members created';
    RAISE NOTICE 'Old table: email_subscribers backed up and removed';
    RAISE NOTICE 'Views created: community_stats, invite_source_stats, recent_community_activity';
    RAISE NOTICE 'Ready for Discord community integration!';
END
$$;