# Asabaal Ventures - Login System Setup Guide

## Overview
This guide walks you through setting up the complete login system with job processing capabilities for Asabaal Ventures.

## Prerequisites
- Python 3.8+ installed
- Supabase account and project
- Node.js 16+ (for frontend)
- Git

## Step 1: Supabase Database Setup

### 1.1 Create/Update Database Schema
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the complete schema from `COMPLETE_DATABASE_SCHEMA.sql`

### 1.2 Create Storage Buckets
Run these commands in the Supabase SQL Editor:
```sql
INSERT INTO storage.buckets (id, name, public) VALUES ('job_files', 'job_files', false);
INSERT INTO storage.buckets (id, name, public) VALUES ('user_uploads', 'user_uploads', false);
INSERT INTO storage.buckets (id, name, public) VALUES ('temp_files', 'temp_files', false);
```

### 1.3 Set Up Storage Policies
```sql
-- Allow authenticated users to upload to job_files
CREATE POLICY "Users can upload job files" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'job_files' AND 
    auth.role() = 'authenticated'
  );

-- Allow users to access their own job files
CREATE POLICY "Users can access own job files" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'job_files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );
```

## Step 2: Worker Daemon Setup

### 2.1 Install Dependencies
```bash
cd prototypes/login_system
pip install -r requirements.txt
```

### 2.2 Configure Environment
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 2.3 Test Worker Connection
```bash
python -c "
from worker_daemon_fixed import JobWorker
try:
    worker = JobWorker()
    print('✅ Worker initialized successfully')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### 2.4 Run Worker Daemon
```bash
python worker_daemon_fixed.py
```

## Step 3: Frontend Integration

### 3.1 Update Supabase Configuration
Update your existing `config/supabase-keys.js`:
```javascript
window.VITE_SUPABASE_URL = 'https://your-project-id.supabase.co';
window.VITE_SUPABASE_ANON_KEY = 'your-anon-key-here';
```

### 3.2 Add Authentication Components
Create authentication components in your existing website structure.

## Step 4: Testing the System

### 4.1 Test Job Submission
1. Create a test user account
2. Submit a test job through the frontend
3. Verify the worker processes it

### 4.2 Monitor System
Check logs and database to ensure everything works:
```bash
tail -f /var/log/asabaal-worker.log
```

## Troubleshooting

### Common Issues

**Worker can't connect to Supabase:**
- Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env
- Check network connectivity
- Ensure service role key has correct permissions

**File upload failures:**
- Verify storage buckets exist
- Check RLS policies on storage objects
- Ensure file size limits are respected

**Jobs not processing:**
- Check worker logs for errors
- Verify job status in database
- Ensure worker is running and polling

### Debug Commands
```bash
# Check worker status
ps aux | grep worker_daemon

# Test database connection
python -c "
from supabase import create_client
import os
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)
print('✅ Database connection successful')
"

# View recent jobs
python -c "
from supabase import create_client
import os
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)
response = client.table('jobs').select('*').order('created_at', desc=True).limit(5).execute()
print(response.data)
"
```

## Security Considerations

1. **Never commit service role keys** to version control
2. **Use HTTPS** for all communications
3. **Implement rate limiting** on job submissions
4. **Validate all file uploads** for size and type
5. **Monitor logs** for suspicious activity

## Production Deployment

### Systemd Service (Linux)
Create `/etc/systemd/system/asabaal-worker.service`:
```ini
[Unit]
Description=Asabaal Ventures Job Worker
After=network.target

[Service]
Type=simple
User=asabaal
WorkingDirectory=/path/to/prototypes/login_system
Environment=PYTHONPATH=/path/to/prototypes/login_system
EnvironmentFile=/path/to/.env
ExecStart=/usr/bin/python3 worker_daemon_fixed.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable asabaal-worker
sudo systemctl start asabaal-worker
sudo systemctl status asabaal-worker
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "worker_daemon_fixed.py"]
```

## Monitoring and Maintenance

### Log Rotation
Add to `/etc/logrotate.d/asabaal-worker`:
```
/var/log/asabaal-worker.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 asabaal asabaal
}
```

### Health Checks
Create a simple health check endpoint:
```python
# Add to worker daemon
def health_check(self):
    try:
        # Test database connection
        self.supabase.table('jobs').select('count').execute()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Next Steps

1. **Integrate existing audio-reactor pipeline** - Replace placeholder FFmpeg command
2. **Integrate PR agent** - Connect your existing code review system
3. **Add monitoring dashboard** - Real-time job status and system metrics
4. **Implement notifications** - Email/discord alerts for job completion
5. **Scale workers** - Multiple worker processes for different job types

## Support

For issues and questions:
1. Check logs first
2. Review this troubleshooting section
3. Consult the implementation plan documentation
4. Test with minimal setup before adding complexity