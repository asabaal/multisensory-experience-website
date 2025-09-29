// Supabase Configuration Template
// Copy this to 'supabase-keys.js' and add your actual credentials
// This file should NOT be committed to git - it's in .gitignore

window.VITE_SUPABASE_URL = 'https://your-project-id.supabase.co';
window.VITE_SUPABASE_ANON_KEY = 'your-anon-key-here';

// Discord webhook for notifications (optional)
window.DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/your-webhook-url';

// Discord invite link for community signups (optional)
window.DISCORD_INVITE_URL = 'https://discord.gg/YourInviteCode';

// Instructions:
// 1. Go to your Supabase project dashboard
// 2. Navigate to Settings → API  
// 3. Copy your Project URL and anon/public key
// 4. Replace the values above with your actual credentials
// 5. Save this file as 'supabase-keys.js' (not .template.js)
//
// Security Note: The anon key is safe to expose publicly - it's designed for frontend use
// Never commit the service role key to your frontend code!