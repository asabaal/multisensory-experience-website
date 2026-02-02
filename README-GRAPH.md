# Website Navigation Graph

## Generated Files

### website-nav-graph.png
- Format: PNG (8000 x 4951 pixels, 160 DPI)
- Size: 4.6MB
- Background: Dark (#1a1a2e)
- Nodes: 75 pages
- Edges: 503 navigation links
- Layout: Neato (force-directed, better horizontal spread)
- Canvas: 50" x 100" (wide aspect ratio)

### website-nav-graph.svg
- Format: SVG (vector)
- Size: 240KB
- Scalable for any resolution

### website-nav.dot
- Graphviz DOT source file
- Can be edited to customize layout

## How to Regenerate

Run the graph generation script:
```bash
python3 generate-nav-graph.py
```

This will:
1. Scan all HTML files in repository
2. Extract internal navigation links (nav, cards, footer, breadcrumbs)
3. Categorize pages by type (entry, modes, content, series, business, etc.)
4. Generate clustered Graphviz DOT file (`website-nav.dot`)
5. Render PNG (8000px wide) and SVG images

## Color Coding

The graph uses color-coded nodes organized into clusters:

### Primary Clusters (Main Sections)
- 🟡 **Entry** (#FFD700): Home page
- 🟣 **Consume Mode** (#8B5CF6): Main consume page + content (Amusements, Blogs, Shows, Games)
- 🔵 **Interact Mode** (#06B6D4): Main interact page + tools (Contest, Revenue, Tic Tac Toe)
- 🟢 **Learn Mode** (#10B981): Main learn page + content (About Founder, What We Do)
- 🟠 **Business Mode** (#F59E0B): Main business page + sub-pages (Products, Services, Partner, Build With Me/You)
- 🟣 **About** (#F472B6/FBCFE8): Asabaal, Projects, Playlists, Advancements, Acts

### Secondary Clusters
- ⚪ **Utility** (#6B7280/9CA3AF): Connect, Links, Privacy, Terms
- 🟪 **Series** (#FB923C/FDBA74): Musical Poetry, Life is Your Word (with seasons/episodes)
- 🟣 **Special** (#C084FC): Vision 2054, Open Source Model
- 🩷 **Blog Posts** (#F9A8D4): All blog/post-*.html files (29 posts)
- 🔴 **Prototypes** (#818CF8): Phase 1-5 prototypes
- 🔵 **Visualizations** (#38BDF8): Ecosystem, Timeline, Power Distribution
- 🟦 **Documentation** (#60A5FA): Resume/CV files

## Edge Styling

- **Primary navigation**: Solid gold (#fbbf24), thick (penwidth=2.5)
- **Secondary links**: Dashed gray (#9CA3AF), thin (penwidth=1.0)

## Layout Details

- **Engine**: Neato (force-directed algorithm)
- **Direction**: Spreads horizontally with better edge flow
- **Spacing**: Reduced vertical separation (ranksep=0.3, nodesep=0.25)
- **Aspect Ratio**: 4.0 width multiplier for wide, horizontal layout
- **Clustering**: Pages grouped by category with colored backgrounds
- **Curve Style**: Curved edges (more organic flow than straight lines)

## Graph Contents

The graph shows complete navigation topology including:
- Main navigation links between all mode pages
- Content card links from hub pages to sub-pages
- Series navigation (Musical Poetry, Life is Your Word with episodes)
- Blog post links
- Footer links and utility pages
- Prototype and visualization files
- Inter-cluster and intra-cluster connections

## File Locations

- Script: `generate-nav-graph.py`
- DOT Data: `website-nav.dot`
- PNG Image: `website-nav-graph.png`
- SVG Image: `website-nav-graph.svg`
- This Doc: `README-GRAPH.md`

## Customization

To customize the graph:

1. Edit `generate-nav-graph.py` to change:
   - DPI (default: 160)
   - Canvas size (default: 50"x100")
   - Aspect ratio (default: 4.0)
   - Colors and categories
   
2. Or edit `website-nav.dot` directly for precise Graphviz control

3. Run `python3 generate-nav-graph.py` to regenerate
