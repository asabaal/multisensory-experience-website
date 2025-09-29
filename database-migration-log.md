# Database Migration Log

This file tracks all SQL changes made to the Supabase database for the Asabaal Ventures website.

## Initial Setup
**Date**: Prior to this log  
**File**: `supabase-minimal-setup.sql`  
**Description**: Initial database setup with contact forms and email subscriptions

**Tables Created**:
- `contact_messages` - Stores contact form submissions
- `email_subscribers` - Stores newsletter subscriptions

**Security**: Row Level Security (RLS) enabled on both tables

---

## Migration 1: Discord Signup Integration
**Date**: 2025-08-02  
**File**: `discord-signup-migration.sql`  
**Description**: Added Discord community signup functionality

**Changes Made**:
```sql
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
```

**New Tables/Views**:
- `discord_members` (view) - Admin view of Discord community members

---

## Migration 2: Security Verification & RLS Fix
**Date**: 2025-08-02  
**File**: N/A (manual verification)  
**Description**: Verify and fix Row Level Security on all tables

**SQL to Run**:
```sql
-- Re-enable RLS on all tables (in case it was disabled)
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_subscribers ENABLE ROW LEVEL SECURITY;

-- Verify current policies exist
SELECT schemaname, tablename, policyname, cmd, roles 
FROM pg_policies 
WHERE tablename IN ('contact_messages', 'email_subscribers');
```

**Expected Result**: All tables should show lock icons in Supabase dashboard

**Status**: ✅ **COMPLETED** - 2025-08-02
**Verification**: All 6 security policies confirmed active:
- contact_messages: 1 policy (INSERT)
- email_subscribers: 5 policies (INSERT, UPDATE, SELECT, Discord INSERT, Discord UPDATE)
- All tables showing lock icons in dashboard

---

## Current Database Schema

### Tables:

#### `contact_messages`
- `id` (UUID, Primary Key)
- `name` (VARCHAR(255), NOT NULL)
- `email` (VARCHAR(255), NOT NULL)
- `subject` (VARCHAR(500))
- `message` (TEXT, NOT NULL)
- `source` (VARCHAR(100), DEFAULT 'website')
- `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW())

#### `email_subscribers`
- `id` (UUID, Primary Key)
- `email` (VARCHAR(255), UNIQUE, NOT NULL)
- `name` (VARCHAR(255))
- `subscription_source` (VARCHAR(100), DEFAULT 'website')
- `status` (VARCHAR(50), DEFAULT 'active')
- `subscribed_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW())
- `unsubscribed_at` (TIMESTAMP WITH TIME ZONE)
- `discord_username` (VARCHAR(255)) - *Added in Migration 1*
- `discord_signup` (BOOLEAN, DEFAULT FALSE) - *Added in Migration 1*
- `source` (VARCHAR(100), DEFAULT 'website') - *Added in Migration 1*

### Views:

#### `discord_members`
- Admin-only view of Discord community members
- Filters `email_subscribers` where `discord_signup = TRUE`

### Security Policies:
- **contact_messages**: Anyone can INSERT
- **email_subscribers**: Anyone can INSERT and UPDATE (for unsubscribes)
- **email_subscribers**: Discord signups can INSERT/UPDATE with `discord_signup = TRUE`

---

## Migration 3: Optional Email for Discord Signups
**Date**: 2025-08-03  
**File**: N/A (manual SQL execution)  
**Description**: Allow NULL email addresses for Discord-only signups

**Issue**: Users should be able to join Discord with just name + Discord username, but database requires email (NOT NULL constraint)

**SQL to Run**:
```sql
-- Remove NOT NULL constraint from email column
ALTER TABLE email_subscribers 
ALTER COLUMN email DROP NOT NULL;

-- Add constraint to ensure data integrity:
-- For Discord signups: discord_username is required
-- For email signups: email is required
ALTER TABLE email_subscribers 
ADD CONSTRAINT check_signup_requirements 
CHECK (
    (discord_signup = TRUE AND discord_username IS NOT NULL) OR
    (discord_signup = FALSE AND email IS NOT NULL) OR
    (discord_signup IS NULL AND email IS NOT NULL)
);

-- Update the unique constraint to handle NULL emails properly
-- (PostgreSQL treats NULL values as unique, so this should work fine)
-- But let's verify the existing constraint first
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'email_subscribers' 
AND constraint_type = 'UNIQUE';
```

**Expected Result**: 
- Email field can now be NULL for Discord-only signups
- Discord signups MUST have discord_username (enforced by constraint)
- Email signups MUST have email (enforced by constraint)
- Existing unique constraint on email handles NULLs properly

**Status**: 🔄 **PENDING EXECUTION**

---

## Notes:
- All tables have Row Level Security (RLS) enabled
- Anonymous users can only perform allowed operations (contact forms, subscriptions, Discord signups)
- Admin access via Supabase dashboard using service role
- No public access to member lists or sensitive data