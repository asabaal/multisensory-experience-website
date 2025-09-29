#!/usr/bin/env python3
"""
Batch Blog Processor with Real-Time Progress Monitoring
Shows live output from Claude processing
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def run_with_live_output(cmd, post_name):
    """Run command and show output in real-time"""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    print(f"\n🔄 LIVE OUTPUT for {post_name}:")
    print("=" * 60)
    
    # Read output line by line as it comes
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"  {line.rstrip()}")
    
    process.wait()
    return process.returncode

def main():
    """Run batch processing with live progress monitoring"""
    
    print("🚀 Batch Blog Processor - VERBOSE MODE")
    print("=" * 60)
    print("📊 This will show real-time progress for each post")
    print("⏱️  Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Check for OAUTH token
    if not os.getenv('CLAUDE_CODE_OAUTH_TOKEN'):
        print("❌ CLAUDE_CODE_OAUTH_TOKEN environment variable not set!")
        print("   Please set it with: export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'")
        sys.exit(1)
    
    # Define all posts to process
    posts_to_process = [
        "asabaal-ventures.md",
        "by-my-hand.md", 
        "charting-the-course-for-a-more-fulfilling-future.md",
        "collaborative-business-models-and-ethical-advertising.md",
        "ethical-advocacy-and-the-future-of-education.md",
        "free-as-a-bird.md",
        "human-creativity-with-ai-and-ethical-social-platforms.md",
        "keep-it-simple.md",
        "logical-fallacies.md",
        "microaggression.md",
        "more-than-me.md",
        "no.md",
        "omniscient.md",
        "power-of-pain.md",
        "probably-right.md",
        "respect-the-fundamental-human-right.md",
        "send-that.md",
        "soundclash.md",
        "special.md",
        "the-future-of-work-and-personal-growth.md",
        "the-unity-of-truth.md",
        "unveiling-the-future-of-asabaal-ventures.md",
        "why.md",
        "your-nature.md"
    ]
    
    # Track results and timing
    successful = []
    failed = []
    start_time = time.time()
    
    # Process each post
    for i, post in enumerate(posts_to_process, 1):
        post_start = time.time()
        
        print(f"\n{'='*60}")
        print(f"📝 STARTING POST {i}/{len(posts_to_process)}: {post}")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # Run with live output
            returncode = run_with_live_output([
                sys.executable, 
                "automated_claude_processor.py", 
                post
            ], post)
            
            post_duration = time.time() - post_start
            
            if returncode == 0:
                print(f"\n✅ SUCCESS: {post} (took {post_duration:.1f} seconds)")
                successful.append(post)
            else:
                print(f"\n❌ FAILED: {post} (took {post_duration:.1f} seconds)")
                failed.append(post)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  INTERRUPTED by user during: {post}")
            failed.append(post)
            break
        except Exception as e:
            print(f"\n🚨 ERROR: {post} - {str(e)}")
            failed.append(post)
        
        # Show progress summary
        total_elapsed = time.time() - start_time
        avg_time = total_elapsed / i
        remaining = len(posts_to_process) - i
        eta = remaining * avg_time
        
        print(f"\n📊 Progress: {i}/{len(posts_to_process)} posts processed")
        print(f"⏱️  Average time per post: {avg_time:.1f} seconds")
        print(f"🔮 Estimated time remaining: {eta/60:.1f} minutes")
    
    # Print final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("🎉 BATCH PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"✅ Successful: {len(successful)} posts")
    print(f"❌ Failed: {len(failed)} posts")
    
    if successful:
        print(f"\n✅ Successfully processed:")
        for post in successful:
            print(f"   - {post}")
    
    if failed:
        print(f"\n❌ Failed to process:")
        for post in failed:
            print(f"   - {post}")
    
    print(f"\n📊 Total: {len(posts_to_process)} posts attempted")
    if len(posts_to_process) > 0:
        print(f"🎯 Success rate: {len(successful)/len(posts_to_process)*100:.1f}%")
    
    if failed:
        print(f"\n💡 Tip: You can retry failed posts individually:")
        for post in failed:
            print(f"   python automated_claude_processor.py {post}")
    
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user (Ctrl+C)")
        sys.exit(1)