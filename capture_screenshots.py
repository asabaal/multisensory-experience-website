#!/usr/bin/env python3
"""
Screenshot Capture System
Capture screenshots of all pages from maintenance log
Process one page at a time with progress tracking
"""

import os
import sys
import csv
import time
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'site_maintenance_log.csv')
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'site_ops', 'screenshots')
BASE_URL = 'file:///mnt/storage/repos/multisensory-experience-website/'

# Screenshot configuration
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
TIMEOUT_MS = 30000
WAIT_FOR_IDLE_MS = 2000
MAX_RETRIES = 2
RETRY_DELAY_MS = 3000

def convert_url_to_filename(page_url: str) -> str:
    """Convert page URL to safe screenshot filename"""
    # Remove .html extension
    name = page_url.replace('.html', '')
    
    # Replace / with _
    name = name.replace('/', '_')
    
    # Replace multiple _ with single _
    while '__' in name:
        name = name.replace('__', '_')
    
    # Add .png extension
    return f"{name}.png"


def get_full_page_path(page_url: str) -> str:
    """Convert relative page URL to full file:// URL"""
    # Normalize path separators
    normalized = page_url.replace('/', os.sep)
    
    # Join with base directory and convert to file:// URL
    full_path = os.path.join(BASE_DIR, normalized)
    
    # Convert to file:// URL for Playwright
    file_url = f"file://{full_path}"
    
    return file_url


def update_csv_with_screenshot(csv_file: str, page_url: str, screenshot_path: str) -> bool:
    """Update CSV with screenshot path for specific page"""
    
    # Read all rows
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find and update the page
    updated = False
    for row in rows:
        if row['Page URL'] == page_url:
            row['Screenshot Path'] = screenshot_path
            updated = True
            break
    
    if not updated:
        print(f"  ⚠ Warning: Page '{page_url}' not found in CSV")
        return False
    
    # Write back all rows
    fieldnames = [
        'Page URL', 'Page Title', 'Page Type', 'Template Used', 'Inbound Links', 'Outbound Links',
        'Human Identified Issues', 'Issue Severity', 'Issue Type', 'Detected By', 'Fix Status', 'PR Link',
        'Last Reviewed Date', 'Video Embed Working', 'Audio Embed Working', 'Image Assets Loaded',
        'Mobile Responsive', 'Screenshot Path'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return True


async def capture_screenshot(page_url: str, browser, screenshot_path: str) -> bool:
    """Capture screenshot of a single page with retry logic"""
    filename = os.path.basename(screenshot_path)
    full_page_url = get_full_page_path(page_url)
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            page = await browser.new_page()
            
            print(f"    Attempt {attempt + 1}/{MAX_RETRIES + 1}")
            
            # Set viewport
            await page.set_viewport_size({
                'width': VIEWPORT_WIDTH,
                'height': VIEWPORT_HEIGHT
            })
            
            # Navigate to page
            print(f"    Navigating to: {page_url}")
            await page.goto(full_page_url, timeout=TIMEOUT_MS, wait_until='networkidle')
            
            # Wait for animations to complete
            print(f"    Waiting for idle ({WAIT_FOR_IDLE_MS}ms)...")
            await asyncio.sleep(WAIT_FOR_IDLE_MS / 1000)
            
            # Capture screenshot
            print(f"    Capturing screenshot...")
            await page.screenshot(
                path=screenshot_path,
                full_page=True,
                type='png'
            )
            
            await page.close()
            print(f"    ✓ Screenshot saved: {screenshot_path}")
            return True
            
        except Exception as e:
            print(f"    ✗ Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < MAX_RETRIES:
                print(f"    Waiting {RETRY_DELAY_MS}ms before retry...")
                await asyncio.sleep(RETRY_DELAY_MS / 1000)
            else:
                print(f"    ✗ All {MAX_RETRIES + 1} attempts failed for {page_url}")
                return False
    
    return False


async def capture_all_screenshots():
    """Main function to capture screenshots for all pages"""
    
    # Ensure screenshots directory exists
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    # Load CSV to get list of pages
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print("=" * 70)
    print("SCREENSHOT CAPTURE SYSTEM")
    print("=" * 70)
    print(f"\n📊 CONFIGURATION:")
    print(f"  CSV File: {CSV_FILE}")
    print(f"  Screenshots Directory: {SCREENSHOTS_DIR}")
    print(f"  Viewport: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Max Retries: {MAX_RETRIES}")
    print(f"  Wait for Idle: {WAIT_FOR_IDLE_MS}ms")
    
    print(f"\n📋 PAGES TO CAPTURE: {len(rows)}")
    
    # Track statistics
    success_count = 0
    failure_count = 0
    skipped_count = 0
    start_time = datetime.now()
    
    async with async_playwright() as p:
        # Launch browser
        print(f"\n🚀 Launching browser...")
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        
        try:
            # Process each page
            for i, row in enumerate(rows, 1):
                page_url = row['Page URL']
                screenshot_filename = convert_url_to_filename(page_url)
                screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
                
                # Check if screenshot already exists
                if os.path.exists(screenshot_path):
                    print(f"\n📸 Page {i}/{len(rows)}: {page_url}")
                    print(f"  ⏭️  Screenshot already exists, skipping...")
                    skipped_count += 1
                    continue
                
                print(f"\n📸 Page {i}/{len(rows)}: {page_url}")
                print(f"  📁 Filename: {screenshot_filename}")
                print(f"  💾 Path: {screenshot_path}")
                
                # Capture screenshot
                success = await capture_screenshot(page_url, browser, screenshot_path)
                
                if success:
                    success_count += 1
                    
                    # Update CSV
                    csv_updated = update_csv_with_screenshot(CSV_FILE, page_url, screenshot_path)
                    if csv_updated:
                        print(f"  ✓ CSV updated with screenshot path")
                    else:
                        print(f"  ⚠ CSV update failed")
                else:
                    failure_count += 1
                
                # Update CSV after each capture
                print(f"  📊 Progress: {i}/{len(rows)} pages ({int(i/len(rows)*100)}%)")
                print(f"  ✓ Success: {success_count}, ✗ Failures: {failure_count}, ⏭️ Skipped: {skipped_count}")
                
                # Small delay between screenshots for stability
                if i < len(rows):
                    await asyncio.sleep(1)
        
        finally:
            # Always close browser
            print(f"\n🔒 Closing browser...")
            await browser.close()
    
    # Final statistics
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("CAPTURE COMPLETE")
    print("=" * 70)
    
    print(f"\n⏱️  Duration: {duration}")
    print(f"\n📊 RESULTS:")
    print(f"  Total Pages: {len(rows)}")
    print(f"  ✓ Successfully Captured: {success_count}")
    print(f"  ✗ Failed: {failure_count}")
    print(f"  ⏭️  Skipped (already exists): {skipped_count}")
    
    if failure_count > 0:
        print(f"\n⚠️  NOTE: {failure_count} pages failed to capture")
        print(f"  Check the console output above for specific error messages")
        print(f"  You can re-run this script to retry failed pages")
    
    print(f"\n📁 Screenshot Directory:")
    print(f"  {SCREENSHOTS_DIR}")
    
    screenshot_files = os.listdir(SCREENSHOTS_DIR)
    print(f"  Total PNG files: {len(screenshot_files)}")
    
    if success_count > 0:
        print(f"\n✅ CSV Updated:")
        print(f"  Screenshot Path column populated for {success_count} pages")
    
    print(f"\n" + "=" * 70)


if __name__ == '__main__':
    asyncio.run(capture_all_screenshots())
