#!/usr/bin/env python3
"""
Capture single screenshot with minimal wait
"""

import os
import csv
import asyncio
from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'site_maintenance_log.csv')
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'site_ops', 'screenshots')

TARGET_PAGE = 'life-is-your-word/season-0.html'
screenshot_filename = "life-is-your-word_season_0.png"
screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
full_page_url = f"file://{BASE_DIR}/{TARGET_PAGE.replace('/', os.sep)}"


async def capture_single_screenshot():
    """Capture screenshot with minimal wait"""
    
    for attempt in range(2):
        try:
            print(f"Attempt {attempt + 1}/2")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
                
                try:
                    page = await browser.new_page()
                    
                    print(f"Navigating to: {TARGET_PAGE}")
                    await page.goto(full_page_url, timeout=45000)
                    
                    print(f"Waiting 2 seconds...")
                    await asyncio.sleep(2)
                    
                    print(f"Capturing screenshot...")
                    await page.screenshot(
                        path=screenshot_path,
                        full_page=True,
                        type='png'
                    )
                    
                    print(f"Screenshot saved: {screenshot_path}")
                    
                    # Update CSV
                    with open(CSV_FILE, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                    
                    updated = False
                    for row in rows:
                        if row['Page URL'] == TARGET_PAGE:
                            row['Screenshot Path'] = screenshot_path
                            updated = True
                            break
                    
                    if updated:
                        fieldnames = [
                            'Page URL', 'Page Title', 'Page Type', 'Template Used', 'Inbound Links', 'Outbound Links',
                            'Human Identified Issues', 'Issue Severity', 'Issue Type', 'Detected By', 'Fix Status', 'PR Link',
                            'Last Reviewed Date', 'Video Embed Working', 'Audio Embed Working', 'Image Assets Loaded',
                            'Mobile Responsive', 'Screenshot Path'
                        ]
                        
                        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(rows)
                        
                        print("CSV updated")
                    else:
                        print("Page not found in CSV")
                    
                    return True
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            await asyncio.sleep(3)
    
    return False


if __name__ == '__main__':
    result = asyncio.run(capture_single_screenshot())
    
    if result:
        print("\n✅ SUCCESS")
    else:
        print("\n❌ FAILED")
