# Supabase Backend Setup Guide

This guide will help you set up the backend infrastructure for the Asabaal Ventures website using Supabase.

## 🚀 Quick Start

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login with your account
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - **Name**: `asabaal-ventures-backend`
   - **Database Password**: Generate a secure password (save this!)
   - **Region**: Choose closest to your users
6. Click "Create new project"

### Step 2: Set Up Database

1. Wait for your project to be ready (2-3 minutes)
2. Go to the **SQL Editor** in your Supabase dashboard
3. Copy the entire contents of `supabase-minimal-setup.sql`
4. Paste it into the SQL Editor
5. Click **Run** to execute all commands

### Step 3: Get Your API Keys

1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy these values (you'll need them later):
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **anon public key** (starts with `eyJhbGciOi...`)
   - **service_role secret key** (starts with `eyJhbGciOi...`) - Keep this secure!

### Step 4: Configure Authentication (Optional)

If you want to access the admin dashboard:

1. Go to **Authentication** → **Settings**
2. Enable **Email** provider
3. Configure email templates if needed
4. Create your admin user:
   - Go to **Authentication** → **Users**
   - Click **Add user**
   - Enter your email and password

## 📋 Database Schema Overview

### Tables Created

1. **`contact_messages`** - Stores contact form submissions
   - `id`, `name`, `email`, `subject`, `message`
   - `source`, `status`, `created_at`, `updated_at`

2. **`email_subscribers`** - Manages email list
   - `id`, `email`, `name`, `subscription_source`
   - `status`, `preferences`, `subscribed_at`, `unsubscribed_at`

3. **`email_campaigns`** - Future email marketing (optional)
   - `id`, `title`, `subject`, `content`
   - `status`, `scheduled_at`, `sent_at`, `recipient_count`

### Security Features

- **Row Level Security (RLS)** enabled on all tables
- Anonymous users can submit contact forms and subscribe
- Only authenticated users can read/manage data
- Automatic duplicate prevention for email subscriptions
- Secure unsubscribe functionality

### Useful Views Created

- `unread_messages_count` - Count of unread messages
- `active_subscribers_count` - Count of active subscribers
- `daily_message_stats` - Daily message statistics
- `subscription_growth` - Subscription growth analytics

## 🔧 Environment Variables

Create a `.env` file in your project root with:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Email Configuration (optional - for future use)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## 🛠️ Testing Your Setup

### Test Database Connection

Run this query in the SQL Editor to verify everything is working:

```sql
-- Check tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check RLS policies
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public';

-- Test data insertion (optional)
INSERT INTO contact_messages (name, email, subject, message) 
VALUES ('Test User', 'test@example.com', 'Test Message', 'This is a test message');

SELECT * FROM contact_messages;
```

### Test API Endpoints

You can test the API endpoints using curl or a tool like Postman:

```bash
# Test contact form submission
curl -X POST 'https://your-project.supabase.co/rest/v1/contact_messages' \
  -H "apikey: your-anon-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com", 
    "subject": "Test Subject",
    "message": "Test message content"
  }'

# Test email subscription
curl -X POST 'https://your-project.supabase.co/rest/v1/email_subscribers' \
  -H "apikey: your-anon-key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "subscriber@example.com",
    "name": "Test Subscriber",
    "subscription_source": "website"
  }'
```

## 📊 Monitoring and Analytics

### View Dashboard Data

Access your data through the Supabase dashboard:

1. **Table Editor** - View and edit data directly
2. **SQL Editor** - Run custom queries
3. **API** - Test API endpoints
4. **Auth** - Manage users

### Useful Queries

```sql
-- Recent messages
SELECT * FROM contact_messages 
ORDER BY created_at DESC 
LIMIT 10;

-- Subscription stats
SELECT 
  subscription_source,
  COUNT(*) as count,
  COUNT(CASE WHEN status = 'active' THEN 1 END) as active
FROM email_subscribers 
GROUP BY subscription_source;

-- Daily activity
SELECT 
  DATE(created_at) as date,
  COUNT(*) as messages
FROM contact_messages 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## 🔒 Security Best Practices

1. **Never expose service role key** in frontend code
2. **Use anon key** for public operations only
3. **Enable email confirmation** for subscribers (optional)
4. **Regularly review** RLS policies
5. **Monitor** for unusual activity
6. **Backup** your database regularly

## 🆘 Troubleshooting

### Common Issues

1. **RLS blocking queries**
   - Check your policies match your use case
   - Verify you're using correct API key

2. **CORS errors**
   - Supabase handles CORS automatically
   - Check your project URL is correct

3. **Insert failures**
   - Check required fields are provided
   - Verify data types match schema

4. **Email duplicates**
   - The system prevents active duplicates automatically
   - Unsubscribed emails can be reactivated

### Getting Help

- Check [Supabase Documentation](https://supabase.com/docs)
- Review SQL error messages in dashboard
- Test API endpoints in the dashboard
- Check browser console for JavaScript errors

## 🚀 Next Steps

After setup is complete:

1. Integrate frontend forms with the API
2. Set up email notifications for new messages
3. Create admin dashboard for managing data
4. Implement email marketing campaigns
5. Add analytics tracking
6. Set up automated backups

---

**Need help?** Check the troubleshooting section or refer to the Supabase documentation.