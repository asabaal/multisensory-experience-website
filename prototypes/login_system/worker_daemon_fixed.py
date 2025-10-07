#!/usr/bin/env python3
"""
Asabaal Ventures - Local Job Worker Daemon (Fixed Version)
Processes jobs from Supabase queue on local machine
Designed for secure, reliable local-first architecture
"""

import os
import sys
import time
import json
import logging
import requests
import hashlib
import tempfile
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from dataclasses import dataclass, field

# Try to import supabase, provide fallback if not available
try:
    from supabase import create_client
except ImportError:
    print("Error: supabase package not installed. Install with: pip install supabase")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/asabaal-worker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobConfig:
    """Configuration for job processing"""
    max_file_size_mb: int = 500
    temp_dir: str = "/tmp/asabaal_jobs"
    supported_audio_formats: List[str] = field(default_factory=lambda: ['.mp3', '.wav', '.flac', '.m4a'])
    supported_video_formats: List[str] = field(default_factory=lambda: ['.mp4', '.avi', '.mov', '.mkv'])

class JobWorker:
    """Main job processing worker"""
    
    def __init__(self):
        self.config = JobConfig()
        self.supabase = self._init_supabase()
        self.worker_id = os.environ.get("WORKER_ID", f"local-{os.getpid()}")
        self.lease_seconds = int(os.environ.get("LEASE_SECONDS", "300"))
        self.poll_interval = int(os.environ.get("POLL_INTERVAL", "3"))
        
        # Ensure temp directory exists
        Path(self.config.temp_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Worker {self.worker_id} initialized")
    
    def _init_supabase(self):
        """Initialize Supabase client"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        return create_client(url, key)
    
    def claim_job(self, app_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Claim a job from the queue"""
        try:
            response = self.supabase.rpc("claim_job", {
                "worker_id": self.worker_id,
                "lease_seconds": self.lease_seconds,
                "app_filter": app_filter
            }).execute()
            
            if response.data and len(response.data) > 0:
                job = response.data[0]
                logger.info(f"Claimed job {job['id']} ({job['app']})")
                return job
            
            return None
            
        except Exception as e:
            logger.error(f"Error claiming job: {e}")
            return None
    
    def extend_lease(self, job_id: str, additional_seconds: int = 300) -> bool:
        """Extend job lease for long-running processes"""
        try:
            response = self.supabase.rpc("extend_job_lease", {
                "job_id": job_id,
                "worker_id": self.worker_id,
                "additional_seconds": additional_seconds
            }).execute()
            
            return response.data if response.data else False
            
        except Exception as e:
            logger.error(f"Error extending lease for job {job_id}: {e}")
            return False
    
    def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """Update job status with optional metadata"""
        try:
            response = self.supabase.rpc("update_job_status", {
                "job_id": job_id,
                "new_status": status,
                "worker_id": self.worker_id,
                **kwargs
            }).execute()
            
            return response.data if response.data else False
            
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return False
    
    def download_file(self, job_id: str, file_kind: str = "input") -> Optional[str]:
        """Download file from Supabase Storage"""
        try:
            # Get file info from database
            response = self.supabase.table("job_files").select("*").eq("job_id", job_id).eq("kind", file_kind).execute()
            
            if not response.data:
                logger.error(f"No {file_kind} file found for job {job_id}")
                return None
            
            file_info = response.data[0]
            storage_path = file_info["storage_path"]
            
            # Download from Supabase Storage
            file_data = self.supabase.storage.from_("job_files").download(storage_path)
            
            # Save to temp file
            temp_path = Path(self.config.temp_dir) / f"{job_id}_{file_kind}{Path(file_info['filename']).suffix}"
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Downloaded {file_kind} file to {temp_path}")
            return str(temp_path)
            
        except Exception as e:
            logger.error(f"Error downloading file for job {job_id}: {e}")
            return None
    
    def upload_file(self, job_id: str, file_path: Union[str, Path], file_kind: str, filename: str = None) -> Optional[str]:
        """Upload file to Supabase Storage"""
        try:
            file_path = Path(file_path)
            if not filename:
                filename = file_path.name
            
            # Generate storage path
            storage_path = f"jobs/{job_id}/{file_kind}/{filename}"
            
            # Upload file
            with open(file_path, 'rb') as f:
                self.supabase.storage.from_("job_files").upload(storage_path, f)
            
            # Get file info
            file_size = file_path.stat().st_size
            checksum = self._calculate_file_checksum(file_path)
            
            # Record in database
            file_record = {
                "job_id": job_id,
                "kind": file_kind,
                "filename": filename,
                "storage_path": storage_path,
                "file_size_bytes": file_size,
                "checksum": checksum
            }
            
            self.supabase.table("job_files").insert(file_record).execute()
            
            # Get public URL
            public_url = self.supabase.storage.from_("job_files").get_public_url(storage_path)
            
            logger.info(f"Uploaded {file_kind} file: {storage_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading file for job {job_id}: {e}")
            return None
    
    def _calculate_file_checksum(self, file_path: Union[str, Path]) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def process_job(self, job: Dict[str, Any]) -> bool:
        """Process a single job"""
        job_id = job["id"]
        app_type = job["app"]
        params = job.get("params", {})
        
        try:
            # Update status to RUNNING
            if not self.update_job_status(job_id, "RUNNING"):
                logger.error(f"Failed to update job {job_id} to RUNNING")
                return False
            
            logger.info(f"Processing job {job_id} ({app_type})")
            
            # Route to appropriate processor
            if app_type == "audio-reactor":
                result_url = self._process_audio_reactor(job_id, params)
            elif app_type == "pr-review":
                result_url = self._process_pr_review(job_id, params)
            else:
                raise ValueError(f"Unknown app type: {app_type}")
            
            if result_url:
                # Mark as completed
                self.update_job_status(
                    job_id, 
                    "COMPLETED", 
                    result_url=result_url,
                    result_metadata={"processed_at": datetime.utcnow().isoformat()}
                )
                logger.info(f"Job {job_id} completed successfully")
                return True
            else:
                raise Exception("Processing failed to produce result")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Job {job_id} failed: {error_msg}")
            
            # Mark as failed
            self.update_job_status(job_id, "FAILED", error_message=error_msg)
            return False
        
        finally:
            # Cleanup temp files
            self._cleanup_temp_files(job_id)
    
    def _process_audio_reactor(self, job_id: str, params: Dict[str, Any]) -> Optional[str]:
        """Process audio-reactor job"""
        logger.info(f"Processing audio-reactor job {job_id}")
        
        # Download input file
        input_file = self.download_file(job_id, "input")
        if not input_file:
            raise Exception("Failed to download input file")
        
        # Extract parameters
        visual_style = params.get("visual_style", "default")
        include_lyrics = params.get("include_lyrics", False)
        output_format = params.get("output_format", "mp4")
        resolution = params.get("resolution", "1080p")
        
        # Generate output filename
        output_filename = f"audio_reactor_{job_id}.{output_format}"
        output_path = Path(self.config.temp_dir) / output_filename
        
        try:
            # Extend lease for long processing
            self.extend_lease(job_id, 600)  # 10 more minutes
            
            # Run audio-reactor pipeline
            if not self._run_audio_reactor_pipeline(
                input_file=input_file,
                output_path=str(output_path),
                visual_style=visual_style,
                include_lyrics=include_lyrics,
                resolution=resolution
            ):
                raise Exception("Audio-reactor pipeline failed")
            
            # Upload result
            result_url = self.upload_file(job_id, output_path, "output", output_filename)
            return result_url
            
        except Exception as e:
            logger.error(f"Audio-reactor processing failed: {e}")
            raise
    
    def _process_pr_review(self, job_id: str, params: Dict[str, Any]) -> Optional[str]:
        """Process PR review job"""
        logger.info(f"Processing PR review job {job_id}")
        
        # Extract parameters
        github_url = params.get("github_url")
        feedback_mode = params.get("feedback_mode", "standard")
        review_depth = params.get("review_depth", "comprehensive")
        
        try:
            # Get code content
            if github_url:
                code_content = self._fetch_github_content(github_url)
            else:
                # Download uploaded code file
                code_file = self.download_file(job_id, "input")
                if not code_file:
                    raise Exception("Failed to download code file")
                
                with open(code_file, 'r') as f:
                    code_content = f.read()
            
            # Run PR agent analysis
            review_result = self._run_pr_agent_analysis(
                code=code_content,
                feedback_mode=feedback_mode,
                review_depth=review_depth
            )
            
            # Save review as markdown
            review_filename = f"pr_review_{job_id}.md"
            review_path = Path(self.config.temp_dir) / review_filename
            
            with open(review_path, 'w') as f:
                f.write(review_result)
            
            # Upload result
            result_url = self.upload_file(job_id, review_path, "output", review_filename)
            return result_url
            
        except Exception as e:
            logger.error(f"PR review processing failed: {e}")
            raise
    
    def _run_audio_reactor_pipeline(self, input_file: str, output_path: str, **kwargs) -> bool:
        """Run the audio-reactor video generation pipeline"""
        try:
            # This is where you integrate your existing audio-reactor pipeline
            # For now, we'll create a placeholder implementation
            
            logger.info(f"Running audio-reactor pipeline: {input_file} -> {output_path}")
            
            # Example FFmpeg command (replace with your actual pipeline)
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-filter:v', 'scale=1920:1080',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return False
            
            # Verify output file exists
            if not Path(output_path).exists():
                logger.error("Output file was not created")
                return False
            
            logger.info("Audio-reactor pipeline completed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Audio-reactor pipeline timed out")
            return False
        except Exception as e:
            logger.error(f"Audio-reactor pipeline error: {e}")
            return False
    
    def _run_pr_agent_analysis(self, code: str, **kwargs) -> str:
        """Run PR agent code analysis"""
        try:
            # This is where you integrate your existing PR agent
            # For now, we'll create a placeholder implementation
            
            logger.info("Running PR agent analysis")
            
            # Placeholder analysis (replace with your actual PR agent)
            analysis = f"""# PR Agent Review Report

Generated: {datetime.utcnow().isoformat()}
Feedback Mode: {kwargs.get('feedback_mode', 'standard')}
Review Depth: {kwargs.get('review_depth', 'comprehensive')}

## Code Summary
- Total lines: {len(code.splitlines())}
- File size: {len(code)} characters

## Analysis Results
### ✅ Strengths
- Code structure appears well-organized
- No obvious syntax errors detected

### 🔍 Areas for Improvement
- Consider adding more comprehensive error handling
- Documentation could be enhanced
- Test coverage should be evaluated

### 📊 Quality Metrics
- Maintainability: Good
- Readability: Good
- Security: No obvious vulnerabilities

## Recommendations
1. Add unit tests for critical functions
2. Consider implementing logging
3. Review for potential performance optimizations

---
*This review was generated by Asabaal Ventures' PR Agent*
"""
            
            return analysis
            
        except Exception as e:
            logger.error(f"PR agent analysis error: {e}")
            raise
    
    def _fetch_github_content(self, github_url: str) -> str:
        """Fetch content from GitHub URL"""
        try:
            # Extract owner, repo, and path from GitHub URL
            # This is a simplified implementation
            api_url = github_url.replace("github.com", "api.github.com/repos") + "/contents"
            
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            # Parse response and extract file content
            # This is simplified - you'd need to handle different GitHub URL formats
            data = response.json()
            
            if isinstance(data, list):
                # Directory listing - get first file
                file_data = data[0] if data else None
            else:
                file_data = data
            
            if not file_data or 'download_url' not in file_data:
                raise Exception("Could not extract file content from GitHub")
            
            # Download actual file content
            file_response = requests.get(file_data['download_url'], timeout=30)
            file_response.raise_for_status()
            
            return file_response.text
            
        except Exception as e:
            logger.error(f"Error fetching GitHub content: {e}")
            raise
    
    def _cleanup_temp_files(self, job_id: str):
        """Clean up temporary files for a job"""
        try:
            temp_dir = Path(self.config.temp_dir)
            for file_path in temp_dir.glob(f"{job_id}_*"):
                file_path.unlink()
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files for job {job_id}: {e}")
    
    def run(self):
        """Main worker loop"""
        logger.info(f"Starting worker {self.worker_id}")
        
        while True:
            try:
                # Claim a job
                job = self.claim_job()
                
                if job:
                    # Process the job
                    self.process_job(job)
                else:
                    # No jobs available, wait
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}")
                time.sleep(self.poll_interval)
        
        logger.info("Worker shutting down")

def main():
    """Entry point"""
    try:
        worker = JobWorker()
        worker.run()
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()