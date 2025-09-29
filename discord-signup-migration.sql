-- Discord Signup Migration
-- Add Discord-related fields to existing email_subscribers table
-- Run this in your Supabase SQL Editor

-- Add Discord-related columns to email_subscribers table
ALTER TABLE email_subscribers 
ADD COLUMN IF NOT EXISTS discord_username VARCHAR(255),
ADD COLUMN IF NOT EXISTS discord_signup BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS source VARCHAR(100) DEFAULT 'website';

-- Update existing records to have source field populated
UPDATE email_subscribers 
SET source = COALESCE(subscription_source, 'website') 
WHERE source IS NULL;

-- Create index for Discord signups (for faster queries)
CREATE INDEX IF NOT EXISTS idx_email_subscribers_discord 
ON email_subscribers (discord_signup) 
WHERE discord_signup = TRUE;

-- Allow Discord signups through the API
-- Note: If policy already exists, you may need to DROP it first
CREATE POLICY "Anyone can signup for Discord" 
ON email_subscribers FOR INSERT 
TO anon 
WITH CHECK (discord_signup = TRUE);

-- Allow upserts for Discord signups (in case someone signs up multiple times)
CREATE POLICY "Allow Discord signup upserts" 
ON email_subscribers FOR UPDATE 
TO anon 
USING (discord_signup = TRUE)
WITH CHECK (discord_signup = TRUE);

-- Optional: Create a view for Discord members (ADMIN USE ONLY)
CREATE OR REPLACE VIEW discord_members AS
SELECT 
    id,
    email,
    name,
    discord_username,
    subscribed_at,
    source
FROM email_subscribers 
WHERE discord_signup = TRUE 
  AND status = 'active'
ORDER BY subscribed_at DESC;

-- DO NOT grant public access to this view!
-- This view is for admin use only via the Supabase dashboard
-- No grants needed - only you (service_role) can access it