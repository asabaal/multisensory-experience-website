#!/usr/bin/env python3
"""
Generate Site Maintenance Log from HTML files and navgraph
Scans pages and creates site_maintenance_log.csv
"""

import os
import re
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOT_FILE = os.path.join(BASE_DIR, 'website-nav.dot')
CSV_OUTPUT = os.path.join(BASE_DIR, 'site_maintenance_log.csv')

def parse_dot_file():
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

def classify_page_type(url, cluster, filepath):
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
    else:
        return 'Content Page'

def detect_template(html_content, url):
    """Detect template used based on patterns"""
    # Check for common template indicators
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
    elif 'visualizations' in url:
        return 'Visualization Template'
    elif '/blog/' in url or 'post-' in url:
        return 'Blog Post Template'
    elif 'musical-poetry' in url or 'life-is-your-word' in url:
        return 'Series Episode Template'
    elif 'resume' in url:
        return 'Resume Template'
    elif '/visualizations/' in url:
        return 'Visualization Template'
    
    return 'Standard Template'

def detect_embeds(html_content):
    """Detect video, audio, and image embeds"""
    # Video embeds
    video_patterns = [
        r'<iframe[^>]*(?:youtube|vimeo|player)',
        r'<video[^>]*>',
        r'youtube\.com/embed',
        r'vimeo\.com/video',
        r'youtube\.com/watch',
        r'<embed[^>]*type="video'
    ]
    
    # Audio embeds
    audio_patterns = [
        r'<audio[^>]*>',
        r'soundcloud\.com',
        r'spotify\.com/embed',
        r'bandcamp\.com',
        r'audio src='
    ]
    
    # Images
    img_patterns = [
        r'<img[^>]+src='
    ]
    
    video_count = sum(len(re.findall(p, html_content, re.IGNORECASE)) for p in video_patterns)
    audio_count = sum(len(re.findall(p, html_content, re.IGNORECASE)) for p in audio_patterns)
    img_count = len(re.findall(img_patterns[0], html_content, re.IGNORECASE))
    
    return video_count, audio_count, img_count

def check_mobile_responsive(html_content):
    """Check if page has mobile responsive design"""
    has_viewport = 'viewport' in html_content.lower()
    has_responsive_css = any([
        '@media' in html_content,
        'flex-wrap' in html_content,
        'grid-template' in html_content,
        'max-width' in html_content,
        'media screen' in html_content
    ])
    
    return has_viewport and has_responsive_css

def extract_title(html_content):
    """Extract page title from HTML"""
    match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ''

def get_full_path(url):
    """Get full file path from URL"""
    # Handle various URL formats
    if '/' in url:
        return os.path.join(BASE_DIR, url)
    else:
        return os.path.join(BASE_DIR, url)

def main():
    """Main execution"""
    print("Generating Site Maintenance Log...")
    
    # Parse DOT file
    print("Parsing navigation graph...")
    nodes, inbound_links, outbound_links = parse_dot_file()
    print(f"  Found {len(nodes)} pages")
    
    # Prepare CSV data
    csv_data = []
    
    # Process each page
    for url, node_info in nodes.items():
        filepath = get_full_path(url)
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"  Warning: File not found: {filepath}")
            continue
        
        # Read HTML file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            print(f"  Error reading {filepath}: {e}")
            continue
        
        # Extract data
        title = extract_title(html_content)
        page_type = classify_page_type(url, node_info['cluster'], filepath)
        template = detect_template(html_content, url)
        video_count, audio_count, img_count = detect_embeds(html_content)
        mobile_responsive = check_mobile_responsive(html_content)
        
        # Count links
        inbound = inbound_links.get(url, 0)
        outbound = outbound_links.get(url, 0)
        
        # Build CSV row
        row = {
            'Page URL': url,
            'Page Title': title,
            'Page Type': page_type,
            'Template Used': template,
            'Inbound Links': inbound,
            'Outbound Links': outbound,
            'Human Identified Issues': '',
            'Issue Severity': '',
            'Issue Type': '',
            'Detected By': 'Automated Scan',
            'Fix Status': '',
            'PR Link': '',
            'Last Reviewed Date': '',
            'Video Embed Working': 'Yes' if video_count > 0 else 'N/A',
            'Audio Embed Working': 'Yes' if audio_count > 0 else 'N/A',
            'Image Assets Loaded': 'Yes' if img_count > 0 else 'N/A',
            'Mobile Responsive': 'Yes' if mobile_responsive else 'No'
        }
        
        csv_data.append(row)
    
    # Sort by URL
    csv_data.sort(key=lambda x: x['Page URL'])
    
    # Write CSV
    print("Writing CSV file...")
    fieldnames = [
        'Page URL',
        'Page Title',
        'Page Type',
        'Template Used',
        'Inbound Links',
        'Outbound Links',
        'Human Identified Issues',
        'Issue Severity',
        'Issue Type',
        'Detected By',
        'Fix Status',
        'PR Link',
        'Last Reviewed Date',
        'Video Embed Working',
        'Audio Embed Working',
        'Image Assets Loaded',
        'Mobile Responsive'
    ]
    
    with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✓ Generated site maintenance log: {CSV_OUTPUT}")
    print(f"  Total pages analyzed: {len(csv_data)}")
    print(f"  CSV columns: {len(fieldnames)}")

if __name__ == '__main__':
    main()
