# 🚀 Vercel Deployment Guide

Your website is ready to deploy with Vercel! Here's the complete setup.

## ✅ What's Already Ready
- ✅ Blog system (static files)
- ✅ All website pages and styling
- ✅ Contact forms and email subscription forms
- ✅ Responsive design

## 🔧 Step 1: Setup Supabase (5 minutes)

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com) → Sign up/Login
2. Click **"New Project"**
3. Name: `asabaal-ventures`
4. Generate password → **Save this password!**
5. Choose region → **Create project** (2-3 minutes)

### 1.2 Setup Database Tables
1. In Supabase dashboard → **SQL Editor**
2. Copy ALL contents from `supabase-minimal-setup.sql`
3. Paste → Click **"Run"**
4. ✅ Done! You now have contact_messages and email_subscribers tables

### 1.3 Get Your API Keys
1. Go to **Settings** → **API**
2. Copy these two values:
   - **Project URL**: `https://xyz.supabase.co`
   - **anon public key**: `eyJhbGciOi...` (long string)

## 🔧 Step 2: Configure Local Development

### 2.1 Add Your Keys Locally
1. Open `config/supabase-keys.js`
2. Replace the placeholder values:

```javascript
// Replace these with your actual values from Supabase
window.VITE_SUPABASE_URL = 'https://your-actual-project-id.supabase.co';
window.VITE_SUPABASE_ANON_KEY = 'your-actual-anon-key-here';
```

### 2.2 Test Locally (Optional)
1. Open `test-forms.html` in your browser
2. Try submitting the contact form
3. Check Supabase dashboard → **Table Editor** → `contact_messages`

**Note:** The `config/supabase-keys.js` file is already in `.gitignore` so your keys won't be committed to GitHub.

## 🚀 Step 3: Deploy to Vercel

### 3.1 Deploy from GitHub
1. Push your code to GitHub (keys won't be included due to .gitignore)
2. Go to [vercel.com](https://vercel.com) → Sign up/Login
3. Click **"New Project"**
4. **Import** your GitHub repository
5. Leave all settings as default:
   - **Framework Preset**: Other
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: (leave empty)

### 3.2 Add Environment Variables in Vercel
1. In Vercel project settings → **Environment Variables**
2. Add these two variables:

```
Name: VITE_SUPABASE_URL
Value: https://your-actual-project-id.supabase.co

Name: VITE_SUPABASE_ANON_KEY  
Value: your-actual-anon-key-here
```

3. Click **"Save"**

### 3.3 Update HTML for Production
You need to update your HTML files to use environment variables in production instead of the local config file.

**Update `index.html` - Replace this section:**
```html
<!-- Local Supabase Configuration -->
<script src="config/supabase-keys.js"></script>
```

**With this:**
```html
<!-- Supabase Configuration -->
<script>
// Use environment variables in production, fallback to local config
if (typeof process !== 'undefined' && process.env) {
    window.VITE_SUPABASE_URL = process.env.VITE_SUPABASE_URL;
    window.VITE_SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY;
}
</script>
<script src="config/supabase-keys.js"></script>
```

**Do the same for `blog.html`**

### 3.4 Deploy!
1. Push changes to GitHub
2. Vercel will automatically redeploy
3. ✅ Your site is live!

## 🧪 Step 4: Test Your Live Site

1. Visit your Vercel URL
2. Try the contact form on your homepage
3. Try the email subscription on your blog page
4. Check Supabase dashboard → **Table Editor** to see submissions

## 📊 Managing Submissions

### View Contact Messages
- Supabase Dashboard → **Table Editor** → `contact_messages`
- You'll see: name, email, subject, message, timestamp

### View Email Subscribers  
- Supabase Dashboard → **Table Editor** → `email_subscribers`
- You'll see: email, name, subscription source, status

### Export Data (Future)
- Click **Export** in Table Editor to download CSV

## 🔒 Security Notes

✅ **Safe to expose publicly:**
- Your anon key (designed for frontend use)
- Your project URL

❌ **Keep private:**
- Your service role key (don't use this in frontend)
- Your database password

## 🔄 Future Updates

### To Update Your Site:
1. Make changes locally
2. Push to GitHub  
3. Vercel auto-deploys

### To Update Supabase:
- Make changes in Supabase dashboard
- No redeployment needed

---

## 🎉 You're Done!

Your website is now live with:
- ✅ Working contact forms
- ✅ Email subscription system  
- ✅ Static blog (fast and reliable)
- ✅ Secure data storage
- ✅ Professional deployment

**Need help?** Check the Vercel logs if forms aren't working, and verify your environment variables are set correctly.