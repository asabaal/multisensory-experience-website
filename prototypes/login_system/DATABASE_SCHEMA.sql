-- Asabaal Ventures - Job Processing System Database Schema
-- Designed for local-first architecture with Supabase

-- ============================================================================
-- USER MANAGEMENT
-- ============================================================================

-- Extended user profile (mirrors Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users_app (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'premium')),
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'premium')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User quotas and limits
CREATE TABLE IF NOT EXISTS public.user_quotas (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  jobs_per_day INTEGER NOT NULL DEFAULT 5,
  max_file_size_mb INTEGER NOT NULL DEFAULT 100,
  storage_quota_mb INTEGER NOT NULL DEFAULT 1000,
  monthly_job_limit INTEGER NOT NULL DEFAULT 50,
  reset_date DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '1 month'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- JOB MANAGEMENT
-- ============================================================================

-- Job status enumeration
CREATE TYPE job_status AS ENUM (
  'QUEUED',      -- Waiting to be processed
  'LEASED',      -- Claimed by worker, processing started
  'RUNNING',     -- Actively being processed
  'COMPLETED',   -- Finished successfully
  'FAILED',      -- Failed with error
  'CANCELLED'    -- Cancelled by user
);

-- Job types enumeration
CREATE TYPE job_app AS ENUM (
  'audio-reactor',    -- Music video generation
  'pr-review',        -- Code review service
  'custom-ai'         -- Future custom AI services
);

-- Main job queue table
CREATE TABLE IF NOT EXISTS public.jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  app job_app NOT NULL,
  params JSONB NOT NULL DEFAULT '{}',
  status job_status NOT NULL DEFAULT 'QUEUED',
  priority INTEGER NOT NULL DEFAULT 100 CHECK (priority >= 1 AND priority <= 1000),
  
  -- Worker leasing system
  leased_by TEXT,
  lease_expires_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Results
  error TEXT,
  result_url TEXT,
  result_metadata JSONB DEFAULT '{}',
  
  -- Idempotency and deduplication
  idempotency_key TEXT,
  
  -- Resource tracking
  estimated_duration_minutes INTEGER,
  actual_duration_minutes INTEGER,
  processing_cost_cents INTEGER DEFAULT 0
);

-- Job file attachments
CREATE TABLE IF NOT EXISTS public.job_files (
  id BIGSERIAL PRIMARY KEY,
  job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK (kind IN ('input', 'output', 'log', 'preview')),
  filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  mime_type TEXT,
  checksum TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Job status history for audit trail
CREATE TABLE IF NOT EXISTS public.job_status_history (
  id BIGSERIAL PRIMARY KEY,
  job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  from_status job_status,
  to_status job_status NOT NULL,
  changed_by TEXT, -- user_id or worker_id
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Jobs table indexes
CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON public.jobs (status, priority ASC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_jobs_user_status ON public.jobs (user_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_lease_expiry ON public.jobs (lease_expires_at) WHERE lease_expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_app_status ON public.jobs (app, status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON public.jobs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_idempotency ON public.jobs (idempotency_key) WHERE idempotency_key IS NOT NULL;

-- Job files indexes
CREATE INDEX IF NOT EXISTS idx_job_files_job_kind ON public.job_files (job_id, kind);
CREATE INDEX IF NOT EXISTS idx_job_files_storage_path ON public.job_files (storage_path);

-- User quotas index
CREATE INDEX IF NOT EXISTS idx_user_quotas_reset_date ON public.user_quotas (reset_date);

-- ============================================================================
-- SECURITY: ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users_app ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_quotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_status_history ENABLE ROW LEVEL SECURITY;

-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON public.users_app
  FOR SELECT USING (auth.uid() = user_id);

-- Users can update their own profile (limited fields)
CREATE POLICY "Users can update own profile" ON public.users_app
  FOR UPDATE USING (auth.uid() = user_id);

-- Service role can manage all users
CREATE POLICY "Service can manage users" ON public.users_app
  FOR ALL USING (auth.role() = 'service_role');

-- Users can view their own quotas
CREATE POLICY "Users can view own quotas" ON public.user_quotas
  FOR SELECT USING (auth.uid() = user_id);

-- Service role can manage quotas
CREATE POLICY "Service can manage quotas" ON public.user_quotas
  FOR ALL USING (auth.role() = 'service_role');

-- Users can view their own jobs
CREATE POLICY "Users can view own jobs" ON public.jobs
  FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own jobs
CREATE POLICY "Users can insert own jobs" ON public.jobs
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own jobs (only certain fields/statuses)
CREATE POLICY "Users can update own jobs" ON public.jobs
  FOR UPDATE USING (
    auth.uid() = user_id AND 
    status IN ('QUEUED', 'CANCELLED')
  );

-- Service role has full access to jobs
CREATE POLICY "Service can manage jobs" ON public.jobs
  FOR ALL USING (auth.role() = 'service_role');

-- Users can view files for their own jobs
CREATE POLICY "Users can view own job files" ON public.job_files
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.jobs 
      WHERE jobs.id = job_files.job_id AND jobs.user_id = auth.uid()
    )
  );

-- Service role can manage all files
CREATE POLICY "Service can manage job files" ON public.job_files
  FOR ALL USING (auth.role() = 'service_role');

-- Users can view status history for their own jobs
CREATE POLICY "Users can view own job history" ON public.job_status_history
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.jobs 
      WHERE jobs.id = job_status_history.job_id AND jobs.user_id = auth.uid()
    )
  );

-- Service role can manage all history
CREATE POLICY "Service can manage job history" ON public.job_status_history
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- WORKER FUNCTIONS ATOMIC JOB CLAIMING
-- ============================================================================

-- Atomic job claiming function with lease management
CREATE OR REPLACE FUNCTION public.claim_job(
  worker_id TEXT,
  lease_seconds INTEGER DEFAULT 300,
  app_filter job_app DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  user_id UUID,
  app job_app,
  params JSONB,
  status job_status,
  priority INTEGER,
  leased_by TEXT,
  lease_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  claimed_job_id UUID;
BEGIN
  -- Update and claim a job atomically
  UPDATE public.jobs
  SET 
    status = 'LEASED',
    leased_by = worker_id,
    lease_expires_at = NOW() + MAKE_INTERVAL(secs => lease_seconds),
    updated_at = NOW()
  WHERE id = (
    SELECT id FROM public.jobs
    WHERE 
      status IN ('QUEUED', 'LEASED')
      AND (status = 'QUEUED' OR lease_expires_at < NOW())
      AND (app_filter IS NULL OR app = app_filter)
    ORDER BY priority ASC, created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED
  )
  RETURNING id INTO claimed_job_id;
  
  -- Return the claimed job details
  RETURN QUERY
  SELECT 
    j.id,
    j.user_id,
    j.app,
    j.params,
    j.status,
    j.priority,
    j.leased_by,
    j.lease_expires_at,
    j.created_at
  FROM public.jobs j
  WHERE j.id = claimed_job_id;
  
  -- Log the status change
  IF claimed_job_id IS NOT NULL THEN
    INSERT INTO public.job_status_history (job_id, from_status, to_status, changed_by, notes)
    VALUES (claimed_job_id, 'QUEUED', 'LEASED', worker_id, 'Job claimed by worker');
  END IF;
END;
$$;

-- Extend job lease for long-running jobs
CREATE OR REPLACE FUNCTION public.extend_job_lease(
  job_id UUID,
  worker_id TEXT,
  additional_seconds INTEGER DEFAULT 300
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  job_exists BOOLEAN;
BEGIN
  -- Verify the job belongs to this worker
  SELECT EXISTS(
    SELECT 1 FROM public.jobs 
    WHERE id = job_id AND leased_by = worker_id AND status = 'LEASED'
  ) INTO job_exists;
  
  IF NOT job_exists THEN
    RETURN FALSE;
  END IF;
  
  -- Extend the lease
  UPDATE public.jobs
  SET 
    lease_expires_at = NOW() + MAKE_INTERVAL(secs => additional_seconds),
    updated_at = NOW()
  WHERE id = job_id;
  
  RETURN TRUE;
END;
$$;

-- Update job status with audit trail
CREATE OR REPLACE FUNCTION public.update_job_status(
  job_id UUID,
  new_status job_status,
  worker_id TEXT DEFAULT NULL,
  error_message TEXT DEFAULT NULL,
  result_url TEXT DEFAULT NULL,
  result_metadata JSONB DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  old_status job_status;
  job_user_id UUID;
BEGIN
  -- Get current status and user_id for audit
  SELECT status, user_id INTO old_status, job_user_id
  FROM public.jobs
  WHERE id = job_id;
  
  IF NOT FOUND THEN
    RETURN FALSE;
  END IF;
  
  -- Update the job
  UPDATE public.jobs
  SET 
    status = new_status,
    error = error_message,
    result_url = result_url,
    result_metadata = result_metadata,
    updated_at = NOW(),
    finished_at = CASE WHEN new_status IN ('COMPLETED', 'FAILED', 'CANCELLED') 
                      THEN NOW() 
                      ELSE finished_at 
                 END,
    started_at = CASE WHEN new_status = 'RUNNING' AND old_status != 'RUNNING'
                      THEN NOW()
                      ELSE started_at
                 END
  WHERE id = job_id;
  
  -- Log the status change
  INSERT INTO public.job_status_history (job_id, from_status, to_status, changed_by, notes)
  VALUES (job_id, old_status, new_status, worker_id, error_message);
  
  -- Update user quota usage if job completed
  IF new_status IN ('COMPLETED', 'FAILED', 'CANCELLED') THEN
    UPDATE public.user_quotas
    SET updated_at = NOW()
    WHERE user_id = job_user_id;
  END IF;
  
  RETURN TRUE;
END;
$$;

-- ============================================================================
-- USER QUOTA MANAGEMENT
-- ============================================================================

-- Check if user can submit a job
CREATE OR REPLACE FUNCTION public.can_submit_job(
  user_id_param UUID,
  app_param job_app,
  file_size_mb INTEGER DEFAULT 0
)
RETURNS TABLE (
  can_submit BOOLEAN,
  reason TEXT,
  jobs_remaining_today INTEGER,
  storage_remaining_mb INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  quota_record RECORD;
  jobs_today INTEGER;
  total_storage_used BIGINT;
BEGIN
  -- Get user's quota
  SELECT * INTO quota_record
  FROM public.user_quotas
  WHERE user_id = user_id_param;
  
  IF NOT FOUND THEN
    -- Create default quota if doesn't exist
    INSERT INTO public.user_quotas (user_id)
    VALUES (user_id_param);
    
    SELECT * INTO quota_record
    FROM public.user_quotas
    WHERE user_id = user_id_param;
  END IF;
  
  -- Reset monthly quota if needed
  IF quota_record.reset_date <= CURRENT_DATE THEN
    UPDATE public.user_quotas
    SET 
      reset_date = CURRENT_DATE + INTERVAL '1 month',
      updated_at = NOW()
    WHERE user_id = user_id_param;
    
    quota_record.reset_date := CURRENT_DATE + INTERVAL '1 month';
  END IF;
  
  -- Count jobs submitted today
  SELECT COUNT(*) INTO jobs_today
  FROM public.jobs
  WHERE 
    user_id = user_id_param
    AND DATE(created_at) = CURRENT_DATE
    AND status != 'CANCELLED';
  
  -- Calculate storage usage
  SELECT COALESCE(SUM(jf.file_size_bytes), 0) INTO total_storage_used
  FROM public.job_files jf
  JOIN public.jobs j ON jf.job_id = j.id
  WHERE j.user_id = user_id_param AND jf.kind = 'output';
  
  -- Check limits
  can_submit := TRUE;
  reason := 'Job submission allowed';
  
  IF jobs_today >= quota_record.jobs_per_day THEN
    can_submit := FALSE;
    reason := 'Daily job limit reached';
  ELSIF file_size_mb > quota_record.max_file_size_mb THEN
    can_submit := FALSE;
    reason := 'File size exceeds limit';
  ELSIF (total_storage_used / 1024 / 1024) + file_size_mb > quota_record.storage_quota_mb THEN
    can_submit := FALSE;
    reason := 'Storage quota exceeded';
  END IF;
  
  jobs_remaining_today := GREATEST(0, quota_record.jobs_per_day - jobs_today);
  storage_remaining_mb := GREATEST(0, quota_record.storage_quota_mb - (total_storage_used / 1024 / 1024));
  
  RETURN NEXT;
END;
$$;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_app_updated_at
  BEFORE UPDATE ON public.users_app
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_user_quotas_updated_at
  BEFORE UPDATE ON public.user_quotas
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at
  BEFORE UPDATE ON public.jobs
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User job summary view
CREATE OR REPLACE VIEW public.user_job_summary AS
SELECT 
  u.user_id,
  u.subscription_tier,
  COUNT(j.id) FILTER (WHERE j.status = 'QUEUED') as queued_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'RUNNING') as running_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'COMPLETED') as completed_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'FAILED') as failed_jobs,
  COUNT(j.id) FILTER (WHERE DATE(j.created_at) = CURRENT_DATE) as jobs_today,
  MAX(j.created_at) as last_job_date
FROM public.users_app u
LEFT JOIN public.jobs j ON u.user_id = j.user_id
GROUP BY u.user_id, u.subscription_tier;

-- System statistics view (admin only)
CREATE OR REPLACE VIEW public.system_stats AS
SELECT 
  COUNT(j.id) as total_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'QUEUED') as queued_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'RUNNING') as running_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'COMPLETED') as completed_jobs,
  COUNT(j.id) FILTER (WHERE j.status = 'FAILED') as failed_jobs,
  COUNT(DISTINCT j.user_id) as unique_users,
  AVG(EXTRACT(EPOCH FROM (j.finished_at - j.started_at))/60) FILTER (WHERE j.finished_at IS NOT NULL) as avg_duration_minutes,
  SUM(j.processing_cost_cents) as total_processing_cost_cents
FROM public.jobs j;

-- ============================================================================
-- SAMPLE DATA FOR TESTING (REMOVE IN PRODUCTION)
-- ============================================================================

-- This section can be uncommented for development/testing
/*
-- Insert test user quota
INSERT INTO public.user_quotas (user_id, jobs_per_day, max_file_size_mb, storage_quota_mb, monthly_job_limit)
VALUES 
  (auth.uid(), 10, 200, 2000, 100)
ON CONFLICT (user_id) DO NOTHING;
*/

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- Grant execute permissions on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
GRANT EXECUTE ON FUNCTION public.can_submit_job(UUID, job_app, INTEGER) TO authenticated;

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;