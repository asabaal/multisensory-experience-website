#!/usr/bin/env python3
"""
Blog Explorer Refresh Tool
Rebuilds blog-data.js from all published posts
"""

import os
import sys
from pathlib import Path

# Import the automated processor
from automated_claude_processor import AutomatedClaudeProcessor

def main():
    """Refresh the blog explorer"""
    print("🔄 Blog Explorer Refresh Tool")
    print("=" * 40)
    print("This will rebuild blog-data.js from all published posts")
    print("=" * 40)
    
    # No OAUTH token needed for this operation
    # Temporarily set a dummy token to bypass the check
    os.environ['CLAUDE_CODE_OAUTH_TOKEN'] = 'dummy-token-for-refresh'
    processor = AutomatedClaudeProcessor(verbose=True, auto_update=False)
    
    # Run the refresh
    success = processor.refresh_blog_explorer()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("Blog explorer has been refreshed with all published posts")
        print("You can now view your updated blog page with all posts")
    else:
        print("\n❌ FAILED!")
        print("Could not refresh blog explorer - check the errors above")

if __name__ == "__main__":
    main()