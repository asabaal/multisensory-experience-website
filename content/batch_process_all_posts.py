#!/usr/bin/env python3
"""
Batch Blog Processor - Process All Raw Input Files
Automatically processes all ready blog posts using the automated Claude processor
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def main():
    """Run batch processing on all blog posts"""
    
    print("🚀 Batch Blog Processor - Processing ALL posts!")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check for OAUTH token
    if not os.getenv('CLAUDE_CODE_OAUTH_TOKEN'):
        print("❌ CLAUDE_CODE_OAUTH_TOKEN environment variable not set!")
        print("   Please set it with: export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'")
        sys.exit(1)
    
    # Define all posts to process (excluding already processed ones)
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
        print(f"📝 PROCESSING POST {i}/{len(posts_to_process)}: {post}")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Run the automated processor
            result = subprocess.run([
                sys.executable, 
                "automated_claude_processor.py", 
                post  # Don't add raw-input/ prefix - the script expects just filename
            ], 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout per post
            )
            
            post_duration = time.time() - post_start
            
            if result.returncode == 0:
                print(f"\n✅ SUCCESS: {post} (took {post_duration:.1f} seconds)")
                successful.append(post)
            else:
                print(f"\n❌ FAILED: {post} (took {post_duration:.1f} seconds)")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
                failed.append(post)
            
            # Show output if available
            if result.stdout:
                print("\nOutput:")
                print(result.stdout)
                
        except subprocess.TimeoutExpired:
            post_duration = time.time() - post_start
            print(f"\n⏰ TIMEOUT: {post} (exceeded 5 minutes, was at {post_duration:.1f} seconds)")
            failed.append(post)
        except Exception as e:
            post_duration = time.time() - post_start
            print(f"\n🚨 ERROR: {post} - {str(e)} (after {post_duration:.1f} seconds)")
            failed.append(post)
        
        # Progress summary
        if i < len(posts_to_process):
            total_elapsed = time.time() - start_time
            avg_time = total_elapsed / i
            remaining = len(posts_to_process) - i
            eta_seconds = remaining * avg_time
            eta_minutes = eta_seconds / 60
            
            print(f"\n📈 Progress: {i}/{len(posts_to_process)} completed")
            print(f"⏱️  Average time per post: {avg_time:.1f} seconds")
            print(f"🔮 Estimated time remaining: {eta_minutes:.1f} minutes")
    
    # Print final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("🎉 BATCH PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes ({total_time:.0f} seconds)")
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
        if len(successful) > 0:
            avg_success_time = total_time / len(successful)
            print(f"⏱️  Average time per successful post: {avg_success_time:.1f} seconds")
    
    if failed:
        print(f"\n💡 Tip: You can retry failed posts individually:")
        for post in failed:
            print(f"   python automated_claude_processor.py raw-input/{post}")

if __name__ == "__main__":
    main()