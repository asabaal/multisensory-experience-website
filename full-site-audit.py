#!/usr/bin/env python3
"""
Comprehensive Site Maintenance Audit
Single script to audit all pages and generate maintenance log
"""

import os
import re
import csv
from pathlib import Path
from datetime import date
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOT_FILE = os.path.join(BASE_DIR, 'website-nav.dot')
CSV_OUTPUT = os.path.join(BASE_DIR, 'site_maintenance_log.csv')

# ===== SECTION 1: DOT FILE PARSING =====

def parse_dot_file() -> Tuple[Dict, Dict, Dict]:
    """Parse DOT file to extract pages, clusters, and link counts"""
    nodes = {}
    edges = []
    current_cluster = None
    
    with open(DOT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Parse clusters
            if 'subgraph cluster_' in line:
                match = re.search(r'subgraph cluster_(\w+)\s*{', line)
                if match:
                    current_cluster = match.group(1).replace('_', ' ')
            
            # Parse node definitions
            elif ' [' in line and 'fillcolor=' in line:
                match = re.search(r'"([^"]+)"\s*\[label="([^"]*)",\s*fillcolor="([^"]+)"\]', line)
                if match:
                    url = match.group(1)
                    label = match.group(2)
                    color = match.group(3)
                    nodes[url] = {
                        'cluster': current_cluster,
                        'color': color,
                        'label': label
                    }
            
            # Parse edges
            elif '->' in line and not line.startswith('//'):
                match = re.search(r'"([^"]+)"\s*->\s*"([^"]+)"', line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    if source in nodes and target in nodes:
                        edges.append((source, target))
    
    # Count inbound/outbound links
    inbound = defaultdict(int)
    outbound = defaultdict(int)
    
    for source, target in edges:
        outbound[source] += 1
        inbound[target] += 1
    
    return nodes, inbound, outbound


# ===== SECTION 2: PAGE CLASSIFICATION =====

def classify_page_type(url: str, cluster: str, filepath: str) -> str:
    """Classify page type based on URL, cluster, and file location"""
    path_parts = filepath.split('/')
    
    # Check directory-based classification
    if '/blog/' in filepath:
        return 'Blog Post'
    elif '/musical-poetry/' in filepath:
        return 'Series Episode'
    elif '/life-is-your-word/' in filepath:
        return 'Series Episode'
    elif '/visualizations/' in filepath:
        return 'Visualization'
    elif '/resume_cv/' in filepath:
        return 'Resume/CV'
    elif '/prototypes/' in filepath:
        return 'Prototype'
    
    # Check URL-based classification
    if url.startswith('blog/post-'):
        return 'Blog Post'
    elif 'musical-poetry' in url:
        return 'Series Episode'
    elif 'life-is-your-word' in url:
        return 'Series Episode'
    elif 'resume_cv' in url:
        return 'Resume/CV'
    
    # Cluster-based classification
    cluster_lower = cluster.lower()
    if cluster_lower == 'entry':
        return 'Entry Point'
    elif 'primary modes' in cluster_lower:
        if 'consume' in url:
            return 'Mode (Consume)'
        elif 'interact' in url:
            return 'Mode (Interact)'
        elif 'learn' in url:
            return 'Mode (Learn)'
        elif 'business' in url:
            return 'Mode (Business)'
        return 'Primary Mode'
    elif cluster_lower == 'content hubs':
        return 'Content Hub'
    elif cluster_lower == 'utility':
        return 'Utility Page'
    elif cluster_lower == 'about':
        return 'About Page'
    elif cluster_lower == 'series':
        return 'Series Hub'
    elif cluster_lower == 'special':
        return 'Special Feature'
    elif cluster_lower == 'visualizations':
        return 'Visualization'
    elif cluster_lower == 'blog posts':
        return 'Blog Post'
    elif cluster_lower == 'prototypes':
        return 'Prototype'
    elif 'learn sub-pages' in cluster_lower:
        return 'Learn Sub-page'
    elif 'business sub-pages' in cluster_lower:
        return 'Business Sub-page'
    elif 'about sub-pages' in cluster_lower:
        return 'About Sub-page'
    elif 'interact sub-pages' in cluster_lower:
        return 'Interactive Sub-page'
    else:
        return 'Content Page'


def detect_template(html_content: str, url: str) -> str:
    """Detect template used based on patterns"""
    if 'mode-selection' in html_content or 'experience-grid' in html_content:
        return 'Mode Selection'
    elif 'amusements-navigation' in html_content or 'amusements-data' in html_content:
        return 'Amusements Hub'
    elif 'blog-data' in html_content:
        return 'Blog Template'
    elif 'supabase' in html_content.lower():
        return 'Supabase Integrated'
    elif 'tic-tac-toe' in html_content or 'game-board' in html_content:
        return 'Game Template'
    elif 'dispatch-revenue' in html_content:
        return 'Revenue Reporting'
    elif '/visualizations/' in url:
        return 'Visualization Template'
    elif '/blog/' in url or 'post-' in url:
        return 'Blog Post Template'
    elif 'musical-poetry' in url or 'life-is-your-word' in url:
        return 'Series Episode Template'
    elif 'resume' in url:
        return 'Resume Template'
    
    return 'Standard Template'


# ===== SECTION 3: HTML ANALYSIS =====

def extract_page_data(filepath: str):
    """Extract all data from HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"  ⚠ Error reading {filepath}: {e}")
        return None
    
    data = {
        'html_content': html_content,
        'title': '',
        'has_h1': False,
        'has_title': False,
        'has_viewport': False,
        'has_responsive_css': False,
        'has_footer_css': False,
        'has_footer_element': False,
        'video_count': 0,
        'youtube_count': 0,
        'vimeo_count': 0,
        'audio_count': 0,
        'image_sources': [],
        'images_without_alt': 0,
        'fixed_width_iframes': 0,
        'is_redirect': False
    }
    
    # Extract title
    title_match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        data['title'] = title_match.group(1).strip()
        data['has_title'] = True
    
    # Check for H1
    if re.search(r'<h1[^>]*>', html_content, re.IGNORECASE):
        data['has_h1'] = True
    
    # Check for viewport meta tag
    if 'viewport' in html_content.lower():
        data['has_viewport'] = True
    
    # Check for responsive CSS
    data['has_responsive_css'] = any([
        '@media' in html_content,
        'max-width' in html_content,
        'grid-template-columns' in html_content,
        'flex-wrap' in html_content
    ])
    
    # Check for footer CSS and element
    if '.footer' in html_content:
        data['has_footer_css'] = True
    if 'class="footer"' in html_content:
        data['has_footer_element'] = True
    
    # Check for redirect
    if 'http-equiv="refresh"' in html_content:
        data['is_redirect'] = True
    
    # Count videos
    data['video_count'] = len(re.findall(r'<(iframe|video)', html_content, re.IGNORECASE))
    
    # YouTube/Vimeo detection
    data['youtube_count'] = len(re.findall(r'youtube\.com/(embed|watch)', html_content, re.IGNORECASE))
    data['vimeo_count'] = len(re.findall(r'vimeo\.com', html_content, re.IGNORECASE))
    
    # Count audios
    data['audio_count'] = len(re.findall(r'<audio', html_content, re.IGNORECASE))
    
    # Extract image sources
    data['image_sources'] = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    
    # Check for missing alt tags
    img_tags = re.findall(r'<img[^>]+>', html_content, re.IGNORECASE)
    data['images_without_alt'] = sum(1 for img in img_tags if 'alt=' not in img.lower())
    
    # Check for fixed-width iframes
    iframes = re.findall(r'<iframe[^>]+width=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    data['fixed_width_iframes'] = sum(1 for width in iframes 
                                       if 'px' in width and not any(unit in width for unit in ['%', 'vw', 'vh', 'em', 'rem']))
    
    return data


def check_image_files_exist(image_sources: List[str], page_url: str) -> Tuple[List[str], int]:
    """Check if referenced image files exist on disk"""
    missing_images = []
    
    for img_src in image_sources:
        # Skip external URLs
        if img_src.startswith('http'):
            continue
        
        # Resolve relative path
        if img_src.startswith('../'):
            # Go up one directory level for each ../
            up_levels = img_src.count('../')
            page_dir = os.path.dirname(page_url)
            
            # Build relative path from page directory
            rel_path = img_src
            for _ in range(up_levels):
                rel_path = rel_path[3:]  # Remove '../'
                page_dir = os.path.dirname(page_dir) if page_dir else '.'
            
            final_path = os.path.join(BASE_DIR, page_dir, rel_path)
        elif img_src.startswith('./'):
            final_path = os.path.join(os.path.dirname(page_url), img_src[2:])
        elif img_src.startswith('/'):
            final_path = os.path.join(BASE_DIR, img_src.lstrip('/'))
        else:
            final_path = os.path.join(BASE_DIR, os.path.dirname(page_url), img_src)
        
        final_path = os.path.normpath(final_path)
        
        if not os.path.exists(final_path):
            missing_images.append(img_src)
    
    return missing_images, len(image_sources)


# ===== SECTION 4: ISSUE DETECTION =====

def detect_issues(page_data: Dict, url: str, missing_images: List[str]) -> List[str]:
    """Detect all issues based on extracted page data"""
    issues = []
    
    if not page_data['has_h1']:
        issues.append("Missing H1 tag - Critical SEO and accessibility issue")
    
    if not page_data['has_title']:
        issues.append("Missing title tag - Critical for SEO")
    
    if not page_data['has_viewport']:
        issues.append("Missing viewport meta tag - Not mobile responsive")
    
    if page_data['images_without_alt'] > 0:
        issues.append(f"{page_data['images_without_alt']} image(s) missing alt tags - Accessibility issue")
    
    if missing_images:
        img_list = ', '.join(missing_images[:3])
        if len(missing_images) > 3:
            img_list += '...'
        issues.append(f"Missing image files: {img_list}")
    
    if page_data['fixed_width_iframes'] > 0:
        issues.append("Video iframes have fixed pixel widths - May cause mobile overflow")
    
    if page_data['has_footer_element'] and not page_data['has_footer_css']:
        issues.append("Footer element referenced but no .footer CSS defined - May cause layout issues")
    
    if page_data['is_redirect']:
        issues.append("This is a redirect page - Consider updating navigation to point directly to destination")
    
    return issues


# ===== SECTION 5: STATUS DETERMINATION =====

def determine_status_fields(page_data: Dict, missing_images: List[str]) -> Dict[str, str]:
    """Determine Yes/No/N/A for status fields"""
    has_videos = page_data['video_count'] > 0 or page_data['youtube_count'] > 0 or page_data['vimeo_count'] > 0
    has_audios = page_data['audio_count'] > 0
    has_images = len(page_data['image_sources']) > 0
    
    video_working = "Yes" if has_videos else "N/A"
    audio_working = "Yes" if has_audios else "N/A"
    
    if has_images:
        image_assets_loaded = "No" if missing_images else "Yes"
    else:
        image_assets_loaded = "N/A"
    
    mobile_responsive = "Yes" if (page_data['has_viewport'] and page_data['has_responsive_css']) else "No"
    
    return {
        'video_working': video_working,
        'audio_working': audio_working,
        'image_assets_loaded': image_assets_loaded,
        'mobile_responsive': mobile_responsive
    }


# ===== SECTION 6: MAIN AUDIT LOOP =====

def audit_all_pages():
    """Main audit function - processes all pages and generates CSV"""
    
    # Step 1: Parse DOT file
    print("Parsing navigation graph...")
    nodes, inbound_links, outbound_links = parse_dot_file()
    print(f"  Found {len(nodes)} pages")
    
    # Step 2: Audit each page
    print("\nAuditing pages...")
    csv_rows = []
    issue_categories = Counter()
    total_pages = len(nodes)
    
    for url, node_info in nodes.items():
        filepath = os.path.join(BASE_DIR, url)
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"  ⚠  File not found: {url}")
            continue
        
        # Extract HTML data
        page_data = extract_page_data(filepath)
        if page_data is None:
            continue
        
        # Classify page
        page_type = classify_page_type(url, node_info['cluster'], filepath)
        template = detect_template(page_data['html_content'], url)
        
        # Check image files
        missing_images, total_images = check_image_files_exist(page_data['image_sources'], url)
        
        # Detect issues
        issues = detect_issues(page_data, url, missing_images)
        
        # Update issue statistics
        if issues:
            for issue in issues:
                if 'H1' in issue:
                    issue_categories['missing_h1_tag'] += 1
                elif 'title tag' in issue and 'Critical for SEO' in issue:
                    issue_categories['missing_title_tag'] += 1
                elif 'image files' in issue:
                    issue_categories['missing_image_files'] += 1
                elif 'alt tag' in issue:
                    issue_categories['missing_alt_tags'] += 1
                elif 'viewport' in issue:
                    issue_categories['missing_viewport_meta'] += 1
                elif 'footer' in issue:
                    issue_categories['missing_footer_css'] += 1
                elif 'redirect' in issue:
                    issue_categories['redirect_page'] += 1
        
        # Determine status fields
        status = determine_status_fields(page_data, missing_images)
        
        # Build CSV row
        row = {
            'Page URL': url,
            'Page Title': page_data['title'],
            'Page Type': page_type,
            'Template Used': template,
            'Inbound Links': inbound_links.get(url, 0),
            'Outbound Links': outbound_links.get(url, 0),
            'Human Identified Issues': '; '.join(issues) if issues else '',
            'Issue Severity': '',
            'Issue Type': '',
            'Detected By': 'Automated Scan',
            'Fix Status': '',
            'PR Link': '',
            'Last Reviewed Date': str(date.today()),
            'Video Embed Working': status['video_working'],
            'Audio Embed Working': status['audio_working'],
            'Image Assets Loaded': status['image_assets_loaded'],
            'Mobile Responsive': status['mobile_responsive']
        }
        
        csv_rows.append(row)
        print(f"  ✓ {url}")
    
    # Step 3: Write CSV
    print(f"\nWriting CSV file...")
    fieldnames = [
        'Page URL', 'Page Title', 'Page Type', 'Template Used', 'Inbound Links', 'Outbound Links',
        'Human Identified Issues', 'Issue Severity', 'Issue Type', 'Detected By', 'Fix Status', 'PR Link',
        'Last Reviewed Date', 'Video Embed Working', 'Audio Embed Working', 'Image Assets Loaded', 'Mobile Responsive'
    ]
    
    with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"  ✓ Generated {CSV_OUTPUT}")
    print(f"  Total pages: {len(csv_rows)}")
    print(f"  Total columns: {len(fieldnames)}")
    
    # Step 4: Print summary statistics
    print_summary(csv_rows, issue_categories)


# ===== SECTION 7: SUMMARY STATISTICS =====

def print_summary(rows: List[Dict], issue_categories: Counter):
    """Print comprehensive audit summary to console"""
    print("\n" + "=" * 60)
    print("SITE MAINTENANCE AUDIT COMPLETE")
    print("=" * 60)
    
    # Total pages
    print(f"\n📊 TOTAL PAGES: {len(rows)}")
    
    # Pages with issues
    pages_with_issues = sum(1 for r in rows if r['Human Identified Issues'])
    print(f"⚠️  PAGES WITH ISSUES: {pages_with_issues} ({int(pages_with_issues/len(rows)*100)}%)")
    print(f"✅ PAGES WITHOUT ISSUES: {len(rows) - pages_with_issues} ({int((len(rows)-pages_with_issues)/len(rows)*100)}%)")
    
    # Issue breakdown
    if issue_categories:
        print(f"\n📋 ISSUE BREAKDOWN:")
        for issue, count in sorted(issue_categories.items(), key=lambda x: -x[1]):
            print(f"  • {issue.replace('_', ' ').title()}: {count}")
    else:
        print(f"\n📋 ISSUE BREAKDOWN: No issues found!")
    
    # Media assets
    video_yes = sum(1 for r in rows if r['Video Embed Working'] == 'Yes')
    video_na = sum(1 for r in rows if r['Video Embed Working'] == 'N/A')
    audio_yes = sum(1 for r in rows if r['Audio Embed Working'] == 'Yes')
    audio_na = sum(1 for r in rows if r['Audio Embed Working'] == 'N/A')
    images_yes = sum(1 for r in rows if r['Image Assets Loaded'] == 'Yes')
    images_no = sum(1 for r in rows if r['Image Assets Loaded'] == 'No')
    images_na = sum(1 for r in rows if r['Image Assets Loaded'] == 'N/A')
    
    print(f"\n🎬 VIDEO EMBEDS:")
    print(f"  Working: {video_yes}")
    print(f"  N/A: {video_na}")
    
    print(f"\n🎵 AUDIO EMBEDS:")
    print(f"  Working: {audio_yes}")
    print(f"  N/A: {audio_na}")
    
    print(f"\n🖼️  IMAGE ASSETS:")
    print(f"  Loaded: {images_yes}")
    print(f"  Missing: {images_no}")
    print(f"  N/A: {images_na}")
    
    # Mobile responsive
    mobile_yes = sum(1 for r in rows if r['Mobile Responsive'] == 'Yes')
    mobile_no = sum(1 for r in rows if r['Mobile Responsive'] == 'No')
    
    print(f"\n📱 MOBILE RESPONSIVE:")
    print(f"  Yes: {mobile_yes} ({int(mobile_yes/len(rows)*100)}%)")
    print(f"  No: {mobile_no} ({int(mobile_no/len(rows)*100)}%)")
    
    print(f"\n📅 PAGES REVIEWED: {len(rows)} on {str(date.today())}")
    
    # High priority issues
    if issue_categories:
        print(f"\n🚨 HIGH PRIORITY ISSUES:")
        high_priority = ['missing_image_files', 'missing_h1_tag', 'missing_viewport_meta']
        for hp in high_priority:
            count = issue_categories.get(hp, 0)
            if count > 0:
                print(f"  • {hp.replace('_', ' ').title()}: {count} pages")
    else:
        print(f"\n🚨 HIGH PRIORITY ISSUES: None")
    
    print(f"\n" + "=" * 60)


# ===== MAIN EXECUTION =====

if __name__ == '__main__':
    audit_all_pages()
