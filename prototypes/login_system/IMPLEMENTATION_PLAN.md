# Asabaal Ventures - Login System Implementation Plan

## Overview
Based on the chat discussion with Dr. Asabaal Horan, this plan outlines the implementation of a secure, reliable local-first job processing system that integrates with the existing Vercel-hosted website. The system will enable users to submit jobs (audio-reactor videos, PR agent reviews) that are processed locally on Dr. Horan's 128GB machine.

## Architecture Summary

### Frontend (Vercel + Next.js)
- **Authentication**: Auth.js with Supabase adapter
- **Job Submission**: React components for app selection and file upload
- **Dashboard**: Real-time job status and result downloads
- **File Handling**: Direct browser → Supabase Storage uploads

### Backend (Supabase)
- **Database**: Postgres with durable job queue
- **Authentication**: User management and session handling
- **Storage**: File uploads and result storage
- **API**: REST endpoints for job management

### Local Worker (Python)
- **Queue Polling**: Securely pulls jobs from Supabase
- **Job Processing**: Audio-reactor and PR-agent workflows
- **Result Upload**: Stores outputs back to Supabase
- **Isolation**: Runs behind firewall, never exposed

## Phase 1: Database & Authentication Setup

### 1.1 Database Schema
```sql
-- Users table (mirrors Supabase auth)
CREATE TABLE users_app (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id),
  role TEXT DEFAULT 'user',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job queue with leasing system
CREATE TYPE job_status AS ENUM ('QUEUED','LEASED','RUNNING','COMPLETED','FAILED');

CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  app TEXT NOT NULL, -- 'audio-reactor' | 'pr-review'
  params JSONB NOT NULL,
  status job_status DEFAULT 'QUEUED',
  priority INT DEFAULT 100,
  leased_by TEXT,
  lease_expires_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  error TEXT,
  result_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- File management
CREATE TABLE job_files (
  id BIGSERIAL PRIMARY KEY,
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  kind TEXT NOT NULL, -- 'input' | 'output' | 'log'
  storage_path TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 1.2 Row Level Security Policies
```sql
-- Users can only see their own jobs
CREATE POLICY "Users can view own jobs" ON jobs
  FOR SELECT USING (auth.uid() = user_id);

-- Only server can insert jobs for authenticated users
CREATE POLICY "Service can insert jobs" ON jobs
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Users can only update their own job metadata (not status)
CREATE POLICY "Users can update own job params" ON jobs
  FOR UPDATE USING (auth.uid() = user_id AND status = 'QUEUED');
```

### 1.3 Atomic Job Claiming Function
```sql
CREATE OR REPLACE FUNCTION claim_job(worker_id TEXT, lease_seconds INT)
RETURNS SETOF jobs
LANGUAGE SQL
AS $$
  UPDATE jobs j
     SET status = 'LEASED',
         leased_by = worker_id,
         lease_expires_at = NOW() + MAKE_INTERVAL(secs => lease_seconds)
   WHERE j.id = (
     SELECT id FROM jobs
      WHERE status IN ('QUEUED','LEASED')
        AND (status = 'QUEUED' OR lease_expires_at < NOW())
      ORDER BY priority ASC, created_at ASC
      LIMIT 1
      FOR UPDATE SKIP LOCKED
   )
   RETURNING *;
$$;
```

## Phase 2: Frontend Implementation

### 2.1 Authentication Integration
- Install Auth.js with Supabase adapter
- Configure OAuth providers (Google, GitHub)
- Create login/register pages
- Implement session management

### 2.2 Job Submission Interface
```jsx
// App Selector Component
const AppSelector = () => {
  const apps = [
    { id: 'audio-reactor', name: 'Audio Reactor Video', description: 'Generate music-reactive visuals' },
    { id: 'pr-review', name: 'PR Agent Review', description: 'AI-powered code review' }
  ];
  
  return (
    <div className="app-grid">
      {apps.map(app => (
        <AppCard key={app.id} app={app} onSelect={handleAppSelect} />
      ))}
    </div>
  );
};
```

### 2.3 File Upload System
- Generate pre-signed URLs from Supabase Storage
- Direct browser uploads (no server bandwidth)
- Progress indicators and error handling
- File validation (size, type, malware scanning)

### 2.4 Job Dashboard
```jsx
const JobDashboard = () => {
  const [jobs, setJobs] = useState([]);
  
  // Real-time polling every 3 seconds
  useEffect(() => {
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="job-list">
      {jobs.map(job => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
};
```

## Phase 3: Local Worker Implementation

### 3.1 Worker Daemon (Python)
```python
import os
import time
import requests
from supabase import create_client

class JobWorker:
    def __init__(self):
        self.supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        )
        self.worker_id = os.environ.get("WORKER_ID", "local-1")
    
    def claim_job(self):
        response = self.supabase.rpc("claim_job", {
            "worker_id": self.worker_id,
            "lease_seconds": 300
        }).execute()
        
        return response.data[0] if response.data else None
    
    def process_job(self, job):
        try:
            # Update status to RUNNING
            self.update_job_status(job["id"], "RUNNING")
            
            # Route to appropriate processor
            if job["app"] == "audio-reactor":
                result_url = self.process_audio_reactor(job)
            elif job["app"] == "pr-review":
                result_url = self.process_pr_review(job)
            else:
                raise ValueError(f"Unknown app: {job['app']}")
            
            # Mark as completed
            self.update_job_status(job["id"], "COMPLETED", result_url)
            
        except Exception as e:
            self.update_job_status(job["id"], "FAILED", error=str(e))
    
    def run(self):
        while True:
            job = self.claim_job()
            if job:
                self.process_job(job)
            else:
                time.sleep(3)  # Polling interval
```

### 3.2 Audio Reactor Processor
```python
def process_audio_reactor(self, job):
    params = job["params"]
    
    # Download input file from Supabase Storage
    input_file = self.download_file(job["id"], "input")
    
    # Process with existing pipeline
    output_path = run_audio_reactor_pipeline(
        input_file=input_file,
        visual_style=params.get("visual_style", "default"),
        include_lyrics=params.get("include_lyrics", False)
    )
    
    # Upload result
    result_url = self.upload_file(job["id"], output_path, "output")
    
    return result_url
```

### 3.3 PR Review Processor
```python
def process_pr_review(self, job):
    params = job["params"]
    
    # Fetch code from GitHub or process uploaded files
    if params.get("github_url"):
        code_content = self.fetch_github_content(params["github_url"])
    else:
        code_content = self.download_file(job["id"], "input")
    
    # Run PR agent analysis
    review_result = run_pr_agent_analysis(
        code=code_content,
        feedback_mode=params.get("feedback_mode", "standard")
    )
    
    # Upload review as markdown
    result_url = self.upload_file(job["id"], review_result, "output")
    
    return result_url
```

## Phase 4: Security & Reliability

### 4.1 Security Measures
- **Input Validation**: Sanitize all user inputs
- **File Scanning**: ClamAV integration for malware detection
- **Rate Limiting**: Per-user quotas (jobs/day, storage limits)
- **Access Control**: RLS policies enforce data isolation
- **Secrets Management**: Environment variables only

### 4.2 Reliability Features
- **Job Leasing**: Prevents duplicate processing
- **Heartbeat System**: Extend leases for long-running jobs
- **Retry Logic**: Exponential backoff for failed jobs
- **Monitoring**: Job metrics and performance tracking
- **Backups**: Automated Supabase backups enabled

### 4.3 Resource Management
```python
# Quota enforcement
def check_user_quota(user_id, app_type):
    quotas = {
        "audio-reactor": {"jobs_per_day": 3, "max_file_size": "100MB"},
        "pr-review": {"jobs_per_day": 10, "max_file_size": "50MB"}
    }
    
    quota = quotas[app_type]
    today_jobs = count_jobs_today(user_id, app_type)
    
    if today_jobs >= quota["jobs_per_day"]:
        raise QuotaExceededError("Daily job limit reached")
    
    return quota
```

## Phase 5: Integration & Deployment

### 5.1 Website Integration
- Add "Login" button to main navigation
- Create dedicated `/dashboard` route
- Update existing contact forms to require auth
- Add job submission CTAs throughout site

### 5.2 Worker Deployment
```bash
# Docker container for isolation
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY worker.py .
CMD ["python", "worker.py"]
```

### 5.3 Environment Configuration
```bash
# .env.local (frontend)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# .env (worker)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
WORKER_ID=local-1
```

## Phase 6: Monitoring & Scaling

### 6.1 Metrics Dashboard
- Job completion rates
- Average processing time per app
- User activity and quotas
- System resource usage

### 6.2 Scaling Path
1. **Stage 1**: Single local worker (current 128GB machine)
2. **Stage 2**: Multiple local workers + cloud overflow
3. **Stage 3**: Full cloud deployment with auto-scaling

### 6.3 Cost Management
- Track processing costs per job type
- Implement usage-based pricing tiers
- Monitor cloud vs local processing economics

## Implementation Timeline

### Week 1: Foundation
- [ ] Set up Supabase project and database schema
- [ ] Implement authentication system
- [ ] Create basic job submission interface

### Week 2: Core Features
- [ ] Build job queue and status tracking
- [ ] Implement file upload/download system
- [ ] Create user dashboard

### Week 3: Worker System
- [ ] Develop local worker daemon
- [ ] Integrate audio-reactor pipeline
- [ ] Integrate PR agent pipeline

### Week 4: Security & Polish
- [ ] Add security measures and rate limiting
- [ ] Implement error handling and retries
- [ ] Create documentation and deployment guides

## Success Metrics

### Technical Metrics
- Job processing success rate > 95%
- Average job completion time < 10 minutes
- System uptime > 99%
- Zero security incidents

### Business Metrics
- User registration conversion rate
- Job submission frequency
- User satisfaction scores
- Cost per job processed

## Next Steps

1. **Immediate**: Set up Supabase project and create database schema
2. **Priority**: Implement authentication and basic job submission
3. **Focus**: Integrate existing audio-reactor and PR-agent workflows
4. **Growth**: Plan scaling path and cost optimization

This implementation provides a secure, reliable foundation for Dr. Horan's vision of distributing power through accessible AI services while maintaining the local-first approach that keeps costs manageable during the early stages.