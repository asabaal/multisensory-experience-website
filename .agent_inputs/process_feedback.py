#!/usr/bin/env python3
"""
Agent Feedback Processing Script

Provides a reproducible workflow for processing agent feedback files
through the Stage 10 feedback update system.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Process agent feedback files")
    parser.add_argument("feedback_file", nargs='?', help="Feedback file to process (relative to pending/)")
    parser.add_argument("--list", "-l", action="store_true", help="List pending feedback files")
    parser.add_argument("--process-all", "-a", action="store_true", help="Process all pending feedback files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    parser.add_argument("--stage10-path", default="/home/asabaal/repos/asabaal-utils/src/asabaal_utils/pr_analyzer/stage10_feedback_updates.py", 
                       help="Path to Stage 10 feedback script")
    
    args = parser.parse_args()
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    stage10_cmd = ["python3", args.stage10_path, "--project-root", str(project_root)]
    
    # Handle different modes
    if args.list:
        print("📝 Listing pending feedback files...")
        result = subprocess.run(stage10_cmd + ["--list"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            sys.exit(1)
        return
    
    elif args.process_all:
        print("🤖 Processing all pending feedback files...")
        if args.dry_run:
            print("🔍 DRY RUN: Would process all pending files")
            return
        
        result = subprocess.run(stage10_cmd + ["--process-all"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings/Errors: {result.stderr}")
        sys.exit(result.returncode)
    
    elif args.feedback_file:
        # Process specific file
        if args.dry_run:
            print(f"🔍 DRY RUN: Would process file: {args.feedback_file}")
            return
        
        print(f"📝 Processing feedback file: {args.feedback_file}")
        result = subprocess.run(stage10_cmd + ["--file", args.feedback_file], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings/Errors: {result.stderr}")
        sys.exit(result.returncode)
    
    else:
        # Show available files
        print("📝 Available feedback files:")
        result = subprocess.run(stage10_cmd + ["--list"], capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0 and "No pending feedback files found" not in result.stdout:
            print("\nUsage:")
            print(f"  {sys.argv[0]} <filename>     Process specific file")
            print(f"  {sys.argv[0]} --list          List pending files")
            print(f"  {sys.argv[0]} --process-all   Process all pending files")
            print(f"  {sys.argv[0]} --dry-run       Show what would be done")
        else:
            print("\n❌ No pending feedback files found")
            print("Create feedback files in .agent_inputs/stage10_feedback/pending/")
        sys.exit(1 if result.returncode != 0 else 0)

if __name__ == "__main__":
    main()