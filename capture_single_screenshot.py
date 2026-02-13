#!/usr/bin/env python3
"""
Capture single screenshot for failed page
"""

import os
import csv
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'site_maintenance_log.csv')
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'site_ops', 'screenshots')
BASE_URL = 'file:///mnt/storage/repos/multisensory-experience-website/'

# Screenshot configuration
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
TIMEOUT_MS = 60000  # 60 seconds (increased from 30)
WAIT_FOR_IDLE_MS = 3000
MAX_RETRIES = 1

TARGET_PAGE = 'life-is-your-word/season-0.html'


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


async def capture_single_screenshot():
    """Capture screenshot of the failed page with extended timeout"""
    
    screenshot_filename = "life-is-your-word_season-0.png"
    screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
    full_page_url = f"file://{BASE_DIR}/{TARGET_PAGE.replace('/', os.sep)}"
    
    print("=" * 70)
    print("SINGLE SCREENSHOT CAPTURE")
    print("=" * 70)
    print(f"\n📊 CONFIGURATION:")
    print(f"  Target Page: {TARGET_PAGE}")
    print(f"  Screenshot Path: {screenshot_path}")
    print(f"  Full URL: {full_page_url}")
    print(f"  Timeout: {TIMEOUT_MS}ms (60 seconds)")
    print(f"  Wait for Idle: {WAIT_FOR_IDLE_MS}ms")
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            print(f"\n🚀 Attempt {attempt + 1}/{MAX_RETRIES + 1}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
                
                try:
                    page = await browser.new_page()
                    
                    await page.set_viewport_size({
                        'width': VIEWPORT_WIDTH,
                        'height': VIEWPORT_HEIGHT
                    })
                    
                    print(f"    Navigating to: {TARGET_PAGE}")
                    await page.goto(full_page_url, timeout=TIMEOUT_MS, wait_until='networkidle')
                    
                    print(f"    Waiting for idle ({WAIT_FOR_IDLE_MS}ms)...")
                    await asyncio.sleep(WAIT_FOR_IDLE_MS / 1000)
                    
                    print(f"    Capturing screenshot...")
                    await page.screenshot(
                        path=screenshot_path,
                        full_page=True,
                        type='png'
                    )
                    
                    await page.close()
                    print(f"    ✓ Screenshot saved: {screenshot_path}")
                    
                    # Update CSV
                    csv_updated = update_csv_with_screenshot(CSV_FILE, TARGET_PAGE, screenshot_path)
                    if csv_updated:
                        print(f"    ✓ CSV updated with screenshot path")
                    else:
                        print(f"    ⚠ CSV update failed")
                    
                    return True
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"    ✗ Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < MAX_RETRIES:
                print(f"    Waiting 5 seconds before retry...")
                await asyncio.sleep(5)
    
    return False


if __name__ == '__main__':
    result = asyncio.run(capture_single_screenshot())
    
    if result:
        print("\n" + "=" * 70)
        print("✅ SCREENSHOT CAPTURE SUCCESSFUL")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ SCREENSHOT CAPTURE FAILED")
        print("=" * 70)
        print("\n⚠️ Could not capture screenshot.")
        print("  The page may have JavaScript issues or infinite loading.")
        print("  You may need to:")
        print("    1. Open the page in a browser manually")
        print("    2. Check if it loads and renders")
        print("    3. Capture screenshot manually")
