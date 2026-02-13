#!/usr/bin/env python3
"""
Extract Website Navigation Graph from HTML Files
Generates clean hierarchical Graphviz visualization with clusters
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOT_OUTPUT = os.path.join(BASE_DIR, 'website-nav.dot')
IMAGE_OUTPUT = os.path.join(BASE_DIR, 'website-nav-graph.png')
SVG_OUTPUT = os.path.join(BASE_DIR, 'website-nav-graph.svg')
DPI = 120

# Define strict hierarchy
CLUSTER_DEFINITION = {
    'Entry': {
        'color': '#FFD700',
        'pages': ['index.html']
    },
    'Primary Modes': {
        'color': '#8B5CF6',
        'subclusters': {
            'Consume': {
                'color': '#8B5CF6',
                'pages': ['consume.html']
            },
            'Interact': {
                'color': '#06B6D4',
                'pages': ['interact.html']
            },
            'Learn': {
                'color': '#10B981',
                'pages': ['learn.html']
            },
            'Business': {
                'color': '#F59E0B',
                'pages': ['do-business.html']
            }
        }
    },
    'Content Hubs': {
        'color': '#A78BFA',
        'pages': ['amusements.html', 'shows.html', 'games.html', 'blogs-selection.html', 'blog.html']
    },
    'Utility': {
        'color': '#6B7280',
        'pages': ['connect.html', 'links.html', 'privacy.html', 'terms.html']
    },
    'About': {
        'color': '#F472B6',
        'pages': ['brands.html']
    },
    'Series': {
        'color': '#FB923C',
        'pages': ['musical-poetry.html', 'life-is-your-word.html']
    },
    'Special': {
        'color': '#C084FC',
        'pages': ['vision_2054_page.html', 'open-source-model.html']
    },
    'Blog Posts': {
        'color': '#F9A8D4',
        'pages': []  # Will collect dynamically
    },
    'Prototypes': {
        'color': '#818CF8',
        'pages': []  # Will collect dynamically
    },
    'Visualizations': {
        'color': '#38BDF8',
        'pages': []  # Will collect dynamically
    },
    'Other': {
        'color': '#E5E7EB',
        'pages': []  # Will collect dynamically
    }
}

def categorize_page(page_path):
    """Categorize a page and get its color"""
    filename = os.path.basename(page_path)
    
    # Direct matches
    for cluster_name, cluster_data in CLUSTER_DEFINITION.items():
        if filename in cluster_data.get('pages', []):
            return cluster_name, cluster_data['color']
    
    # Dynamic categorization
    if 'blog/post-' in page_path:
        return 'Blog Posts', '#F9A8D4'
    if 'prototypes/' in page_path:
        return 'Prototypes', '#818CF8'
    if 'visualizations/' in page_path:
        return 'Visualizations', '#38BDF8'
    if 'resume_cv' in page_path:
        return 'Other', '#60A5FA'
    if 'musical-poetry/' in page_path or filename == 'musical-poetry/season-1/episode-1.html':
        return 'Series', '#FDBA74'
    if 'life-is-your-word/' in page_path:
        return 'Series', '#FDBA74'
    
    # Content under modes
    if 'amusements' in filename or 'shows' in filename or 'games' in filename:
        return 'Content Hubs', '#A78BFA'
    if 'blog' in filename:
        return 'Content Hubs', '#A78BFA'
    
    # Learn sub-pages
    if 'about-founder' in page_path:
        return 'Learn Sub-pages', '#34D399'
    if 'what-we-do' in page_path:
        return 'Learn Sub-pages', '#34D399'
    
    # Business sub-pages
    if 'products' in filename and filename != 'products.html':
        return 'Business Sub-pages', '#FBBF24'
    if 'services' in filename:
        return 'Business Sub-pages', '#FBBF24'
    if 'partner' in filename:
        return 'Business Sub-pages', '#FBBF24'
    if 'build-with' in page_path:
        return 'Business Sub-pages', '#FCD34D'
    
    # About sub-pages
    if 'asabaal.html' in page_path:
        return 'About Sub-pages', '#F472B6'
    if 'asabaal-projects' in page_path or 'playlists' in page_path:
        return 'About Sub-pages', '#FBCFE8'
    if 'advancements' in page_path or 'acts-of' in page_path:
        return 'About Sub-pages', '#FBCFE8'
    
    # Interactive
    if 'dispatch-revenue' in page_path:
        return 'Interact Sub-pages', '#67E8F9'
    if 'unity-remix' in page_path:
        return 'Interact Sub-pages', '#67E8F9'
    if 'tic-tac-toe' in page_path:
        return 'Interact Sub-pages', '#67E8F9'
    
    return 'Other', '#E5E7EB'

def extract_links(html_file):
    """Extract internal href links from HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE)
    
    internal_links = []
    for link in links:
        if link.startswith(('#', 'javascript:', 'mailto:', 'tel:', 'http:', 'https:')):
            continue
        if not link or link.strip() == '':
            continue
        internal_links.append(link)
    
    return internal_links

def get_relative_path(full_path, base_dir):
    """Get path relative to base directory"""
    return str(Path(full_path).relative_to(base_dir))

def build_navigation_graph():
    """Scan all HTML files and build navigation graph"""
    graph = defaultdict(set)
    page_info = {}
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'prototypes', 'development-archive', 'visualizations-archive']]
        
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                node_name = get_relative_path(html_path, BASE_DIR)
                
                cluster_name, color = categorize_page(html_path)
                page_info[node_name] = {
                    'cluster': cluster_name,
                    'color': color,
                    'label': os.path.basename(node_name)
                }
                
                try:
                    links = extract_links(html_path)
                    for link in links:
                        if link.startswith('../'):
                            resolved = os.path.normpath(os.path.join(os.path.dirname(node_name), link))
                            graph[node_name].add(resolved)
                        elif link.startswith('/') or link.startswith('./'):
                            resolved = os.path.normpath(link.lstrip('/.'))
                            graph[node_name].add(resolved)
                        else:
                            graph[node_name].add(link)
                except Exception as e:
                    print(f"Error processing {html_path}: {e}", file=sys.stderr)
    
    return graph, page_info

def generate_dot_file(graph, page_info):
    """Generate clean hierarchical DOT file"""
    dot_content = '''digraph WebsiteNavigation {
    rankdir=LR;
    bgcolor="#1a1a2e";
    fontname="Arial";
    fontsize=10;
    splines=curved;
    overlap=false;
    compound=true;
    ranksep=0.2;
    nodesep=0.1;
    rankdir=LR;
    newrank=true;
    
    // Node styles
    node [fontname="Arial", fontsize=8, fontcolor="white", style="rounded,filled", penwidth=1.0];
    
    // Edge styles
    edge [fontname="Arial", fontsize=7, color="#9CA3AF", penwidth=1.0, arrowsize=0.7];
'''

    # Group pages by cluster
    clusters = defaultdict(list)
    for page, info in page_info.items():
        clusters[info['cluster']].append((page, info))
    
    # Define clusters in order
    cluster_order = [
        'Entry',
        'Primary Modes',
        'Content Hubs',
        'Utility',
        'About',
        'About Sub-pages',
        'Series',
        'Special',
        'Blog Posts',
        'Prototypes',
        'Visualizations',
        'Learn',
        'Learn Sub-pages',
        'Business',
        'Business Sub-pages',
        'Interact',
        'Interact Sub-pages',
        'Other'
    ]
    
    cluster_colors = {
        'Entry': '#FFD700',
        'Primary Modes': '#8B5CF6',
        'Content Hubs': '#A78BFA',
        'Utility': '#6B7280',
        'About': '#F472B6',
        'About Sub-pages': '#FBCFE8',
        'Series': '#FB923C',
        'Special': '#C084FC',
        'Blog Posts': '#F9A8D4',
        'Prototypes': '#818CF8',
        'Visualizations': '#38BDF8',
        'Learn': '#10B981',
        'Learn Sub-pages': '#34D399',
        'Business': '#F59E0B',
        'Business Sub-pages': '#FBBF24',
        'Interact': '#06B6D4',
        'Interact Sub-pages': '#67E8F9',
        'Other': '#E5E7EB'
    }
    
    # Generate clusters
    for cluster_name in cluster_order:
        if cluster_name in clusters:
            pages = clusters[cluster_name]
            if len(pages) > 0:
                cluster_color = cluster_colors.get(cluster_name, '#4c1d95')
                
                dot_content += f'''
    subgraph cluster_{cluster_name.replace(" ", "_")} {{
        style=filled;
        color="{cluster_color}";
        fillcolor="#2d2d3d";
        penwidth=1.5;
        fontsize=12;
        fontname="Arial Bold";
        fontcolor="white";
        label="{cluster_name}";
        rank=same;
'''
                
                # Add nodes
                for page, info in sorted(pages):
                    label = info['label']
                    color = info['color']
                    dot_content += f'        "{page}" [label="{label}", fillcolor="{color}"];\n'
                
                dot_content += '    }\n'

    # Add edges
    edge_count = 0
    for source in sorted(graph.keys()):
        source_info = page_info.get(source, {})
        source_cluster = source_info.get('cluster', 'Other')
        
        for target in sorted(graph[source]):
            if target in page_info:
                target_info = page_info.get(target, {})
                target_cluster = target_info.get('cluster', 'Other')
                
                # Determine edge style based on cluster relationship
                if source_cluster == 'Entry':
                    style = 'solid'
                    color = '#fbbf24'
                    penwidth = '2.5'
                elif source_cluster == 'Primary Modes' and target_cluster == 'Primary Modes':
                    style = 'solid'
                    color = '#fbbf24'
                    penwidth = '2.0'
                elif source_cluster == 'Content Hubs' and target_cluster == 'Series':
                    style = 'solid'
                    color = '#9CA3AF'
                    penwidth = '1.5'
                elif source_cluster == target_cluster:
                    style = 'dashed'
                    color = '#6B7280'
                    penwidth = '0.5'
                else:
                    style = 'solid'
                    color = '#9CA3AF'
                    penwidth = '1.0'
                
                if source_cluster != target_cluster:
                    edge_count += 1
                    if style == 'dashed':
                        dot_content += f'    "{source}" -> "{target}" [style={style}, color="{color}", penwidth={penwidth}];\n'
                    else:
                        dot_content += f'    "{source}" -> "{target}" [color="{color}", penwidth={penwidth}];\n'

    dot_content += '}\n'
    
    return dot_content, edge_count

def main():
    """Main execution"""
    print("Building clean hierarchical navigation graph...")
    
    graph, page_info = build_navigation_graph()
    dot_content, edge_count = generate_dot_file(graph, page_info)
    
    with open(DOT_OUTPUT, 'w') as f:
        f.write(dot_content)
    
    print(f"✓ Extracted {len(page_info)} pages with {edge_count} links")
    print(f"✓ Organized into clusters")
    print(f"✓ DOT file: {DOT_OUTPUT}")
    
    # Visualization disabled - PNG generation skipped
    # Uncomment to enable: dot -Tpng -Gdpi={DPI} -Gratio=3.0 -Gbgcolor="#1a1a2e" {DOT_OUTPUT} -o {IMAGE_OUTPUT}
    print("✓ Visualization disabled - run manually: dot -Tpng website-nav.dot -o website-nav-graph.png")

if __name__ == '__main__':
    main()
