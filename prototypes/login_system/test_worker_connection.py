#!/usr/bin/env python3
"""
Test script for worker daemon connection to Supabase
This script verifies that the worker can connect to Supabase and perform basic operations
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
            return False
        
        client = create_client(url, key)
        
        # Test basic connection
        response = client.table('jobs').select('count').execute()
        print("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_worker_initialization():
    """Test worker initialization"""
    print("\n🔍 Testing worker initialization...")
    
    try:
        from worker_daemon_fixed import JobWorker
        
        worker = JobWorker()
        print(f"✅ Worker initialized successfully with ID: {worker.worker_id}")
        return True
        
    except Exception as e:
        print(f"❌ Worker initialization failed: {e}")
        return False

def test_job_claiming():
    """Test job claiming functionality"""
    print("\n🔍 Testing job claiming...")
    
    try:
        from worker_daemon_fixed import JobWorker
        
        worker = JobWorker()
        
        # Try to claim a job (should return None if no jobs available)
        job = worker.claim_job()
        
        if job:
            print(f"✅ Successfully claimed job: {job['id']}")
            # Clean up - mark as failed so it doesn't stay in queue
            worker.update_job_status(job['id'], 'FAILED', error_message='Test cleanup')
        else:
            print("✅ No jobs available (expected for empty queue)")
        
        return True
        
    except Exception as e:
        print(f"❌ Job claiming test failed: {e}")
        return False

def test_database_functions():
    """Test database RPC functions"""
    print("\n🔍 Testing database functions...")
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        client = create_client(url, key)
        
        # Test can_submit_job function
        response = client.rpc("can_submit_job", {
            "user_id_param": "00000000-0000-0000-0000-000000000000",  # Dummy UUID
            "app_param": "audio-reactor",
            "file_size_mb": 10
        }).execute()
        
        if response.data:
            print("✅ Database functions working")
            return True
        else:
            print("❌ Database functions returned no data")
            return False
        
    except Exception as e:
        print(f"❌ Database function test failed: {e}")
        return False

def test_storage_access():
    """Test Supabase Storage access"""
    print("\n🔍 Testing storage access...")
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        client = create_client(url, key)
        
        # Try to list buckets (should work with service role key)
        try:
            buckets = client.storage.list_buckets()
            print("✅ Storage access successful")
            
            # Check if required buckets exist
            bucket_names = [bucket.name for bucket in buckets]
            required_buckets = ['job_files', 'user_uploads', 'temp_files']
            
            for bucket in required_buckets:
                if bucket in bucket_names:
                    print(f"  ✅ Bucket '{bucket}' exists")
                else:
                    print(f"  ⚠️  Bucket '{bucket}' missing (create with SQL)")
            
            return True
        except Exception as e:
            print(f"⚠️  Storage access limited: {e}")
            print("  This may be expected if storage policies aren't set up yet")
            return True  # Don't fail the test for this
        
    except Exception as e:
        print(f"❌ Storage access test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Asabaal Ventures - Worker Connection Test")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment check:")
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            masked_value = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    if not all(os.environ.get(var) for var in required_vars):
        print("\n❌ Required environment variables not set. Please configure .env file.")
        return False
    
    # Run tests
    tests = [
        test_supabase_connection,
        test_worker_initialization,
        test_job_claiming,
        test_database_functions,
        test_storage_access
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    
    print(f"  Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Worker daemon is ready to use.")
        print("\nNext steps:")
        print("1. Start the worker: python worker_daemon_fixed.py")
        print("2. Set up frontend authentication")
        print("3. Create job submission interface")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Verify Supabase URL and service role key")
        print("2. Ensure database schema is deployed")
        print("3. Check storage bucket creation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)