#!/usr/bin/env python3
"""
Simple Batch Processor - Shows Full Output for Each Post
Just runs the automated processor on each file and shows all the detailed output
"""

import os
import sys
from pathlib import Path

# Import the automated processor directly
from automated_claude_processor import AutomatedClaudeProcessor

def main():
    """Run the automated processor on all posts with full output"""
    
    print("🚀 Simple Batch Blog Processor")
    print("=" * 60)
    print("This will show full detailed output for each post")
    print("=" * 60)
    
    # Check for OAUTH token
    if not os.getenv('CLAUDE_CODE_OAUTH_TOKEN'):
        print("❌ CLAUDE_CODE_OAUTH_TOKEN environment variable not set!")
        print("   Please set it with: export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'")
        sys.exit(1)
    
    # Create processor instance with auto-update enabled
    processor = AutomatedClaudeProcessor(verbose=True, auto_update=True)
    
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
    
    # Track results
    successful = []
    failed = []
    
    # Process each post
    for i, post in enumerate(posts_to_process, 1):
        print(f"\n{'#'*60}")
        print(f"# POST {i} of {len(posts_to_process)}")
        print(f"# File: {post}")
        print(f"{'#'*60}\n")
        
        try:
            # Process the file - this will show all the detailed output
            result = processor.process_file(post)
            
            if result and result.get('html'):
                successful.append(post)
                print(f"\n✨ Post {i}/{len(posts_to_process)} completed successfully!")
            else:
                failed.append(post)
                print(f"\n❌ Post {i}/{len(posts_to_process)} failed!")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  INTERRUPTED by user during: {post}")
            print("Exiting batch processing...")
            break
        except Exception as e:
            print(f"\n🚨 ERROR processing {post}: {str(e)}")
            failed.append(post)
        
        # Add a separator between posts
        if i < len(posts_to_process):
            print(f"\n{'─'*60}")
            print(f"Completed: {i}/{len(posts_to_process)} | Success: {len(successful)} | Failed: {len(failed)}")
            print(f"{'─'*60}\n")
    
    # Print final summary
    print("\n" + "="*60)
    print("🎉 BATCH PROCESSING COMPLETE!")
    print("="*60)
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user (Ctrl+C)")
        sys.exit(1)