# Website Navigation Topological Inventory - Visualization Guide

This directory contains the complete navigation topological inventory for the multisensory-experience-website, with multiple formats for visualization and analysis.

## Files Created

### 1. `NAVIGATION_INVENTORY.md`
**Complete documentation** of the website navigation structure.
- Executive summary
- Navigation hierarchy breakdown
- Branch analysis for each mode
- Special sections documentation
- External link categories
- Incoming link analysis
- Navigation types identified
- Page categorization
- Metrics and recommendations

### 2. `navigation-graph.dot`
**Graphviz DOT format** - Directed graph definition for creating visualizations.
- Complete node definitions with 70+ pages
- Edge definitions with 400+ navigation links
- Color-coded by category
- Clustered by section
- Edge types: primary, secondary, external
- Ready for Graphviz rendering

### 3. `navigation-graph.json`
**JSON format** - Structured data for web-based visualization libraries.
- Nodes with metadata (type, category, level, color, URL)
- Edges with properties (source, target, type, weight, color)
- External node definitions
- Ready for D3.js, Cytoscape.js, Sigma.js, etc.

## How to Visualize

### Option 1: Using Graphviz (DOT file)

**Install Graphviz:**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from https://graphviz.org/download/
```

**Generate PNG:**
```bash
dot -Tpng navigation-graph.dot -o navigation-graph.png
```

**Generate SVG (recommended for web):**
```bash
dot -Tsvg navigation-graph.dot -o navigation-graph.svg
```

**Generate PDF:**
```bash
dot -Tpdf navigation-graph.dot -o navigation-graph.pdf
```

**Generate interactive HTML:**
```bash
dot -Tcmapx -o navigation-graph.map navigation-graph.dot
dot -Tsvg -o navigation-graph.svg navigation-graph.dot
# Then use a tool to create interactive HTML with SVG + image map
```

**Advanced Graphviz Options:**

Different layouts:
```bash
# Force-directed
fdp -Tpng navigation-graph.dot -o navigation-fdp.png

# Radial
twopi -Tpng navigation-graph.dot -o navigation-radial.png

# Circular
circo -Tpng navigation-graph.dot -o navigation-circular.png

# Hierarchical (default)
dot -Tpng navigation-graph.dot -o navigation-hierarchical.png
```

High resolution:
```bash
dot -Tpng -Gdpi=300 navigation-graph.dot -o navigation-graph-hires.png
```

Custom styling:
```bash
dot -Tsvg -Gratio=0.6 -Gnodesep=0.1 -Granksep=0.5 navigation-graph.dot -o navigation-graph-custom.svg
```

### Option 2: Using D3.js (JSON file)

Create an HTML file with D3.js:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Navigation Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { margin: 0; }
        svg { width: 100vw; height: 100vh; }
        .node circle { stroke: #fff; stroke-width: 1.5px; }
        .node text { font: 10px Arial; pointer-events: none; }
        .link { stroke: #999; stroke-opacity: 0.6; }
    </style>
</head>
<body>
    <script>
        fetch('navigation-graph.json')
            .then(response => response.json())
            .then(data => {
                const svg = d3.select("svg");
                const width = window.innerWidth;
                const height = window.innerHeight;

                const simulation = d3.forceSimulation(data.nodes)
                    .force("link", d3.forceLink(data.edges).id(d => d.id))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collide", d3.forceCollide().radius(30));

                const link = svg.append("g")
                    .selectAll("line")
                    .data(data.edges)
                    .join("line")
                    .attr("class", "link")
                    .attr("stroke", d => d.color)
                    .attr("stroke-width", d => d.weight);

                const node = svg.append("g")
                    .selectAll("g")
                    .data(data.nodes)
                    .join("g")
                    .attr("class", "node")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

                node.append("circle")
                    .attr("r", 10)
                    .attr("fill", d => d.color);

                node.append("text")
                    .text(d => d.label)
                    .attr("x", 12)
                    .attr("y", 3);

                simulation.on("tick", () => {
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);

                    node.attr("transform", d => `translate(${d.x},${d.y})`);
                });

                function dragstarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }

                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }

                function dragended(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            });
    </script>
</body>
</html>
```

### Option 3: Using Online Graph Visualization Tools

**Graphviz Online:**
1. Visit https://dreampuf.github.io/GraphvizOnline/
2. Copy and paste `navigation-graph.dot`
3. Adjust settings as needed
4. Export as PNG, SVG, or share URL

**Edotor:**
1. Visit https://edotor.net/
2. Select "dot" as engine
3. Paste the DOT file content
4. Preview and export

**Viz.js:**
1. Visit https://viz-js.com/
2. Paste DOT file content
3. Generate visualization
4. Export or embed

**yEd Live:**
1. Visit https://www.yedlive.com/
2. Import the DOT file
3. Customize visualization
4. Export in multiple formats

### Option 4: Using Python (NetworkX + Matplotlib)

```python
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Load JSON data
import json
with open('navigation-graph.json', 'r') as f:
    data = json.load(f)

# Create graph
G = nx.DiGraph()

# Add nodes with attributes
for node in data['nodes']:
    G.add_node(node['id'],
               label=node['label'],
               color=node['color'],
               type=node['type'],
               category=node['category'],
               level=node['level'])

# Add edges with attributes
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'],
               weight=edge['weight'],
               color=edge['color'],
               type=edge['type'])

# Set node colors
colors = [G.nodes[n]['color'] for n in G.nodes()]
sizes = [300 if G.nodes[n]['type'] == 'entry' else 100 for n in G.nodes()]

# Draw
plt.figure(figsize=(20, 16))
pos = nx.spring_layout(G, k=1, iterations=50)

nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes)
nx.draw_networkx_edges(G, pos, edge_color=[G.edges[e]['color'] for e in G.edges()],
                       width=[G.edges[e]['weight'] for e in G.edges()],
                       arrows=True, arrowsize=20)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

plt.title("Website Navigation Topology")
plt.axis('off')
plt.tight_layout()
plt.savefig('navigation-graph-python.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Option 5: Using Cytoscape.js

```html
<!DOCTYPE html>
<html>
<head>
    <title>Navigation Graph - Cytoscape.js</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <style>
        #cy { width: 100%; height: 100vh; position: absolute; top: 0; left: 0; }
    </style>
</head>
<body>
    <div id="cy"></div>
    <script>
        fetch('navigation-graph.json')
            .then(response => response.json())
            .then(data => {
                const cy = cytoscape({
                    container: document.getElementById('cy'),
                    elements: {
                        nodes: data.nodes.map(n => ({
                            data: {
                                id: n.id,
                                label: n.label,
                                type: n.type,
                                category: n.category,
                                color: n.color
                            }
                        })),
                        edges: data.edges.map(e => ({
                            data: {
                                id: e.source + '-' + e.target,
                                source: e.source,
                                target: e.target,
                                weight: e.weight,
                                color: e.color
                            }
                        }))
                    },
                    style: [
                        {
                            selector: 'node',
                            style: {
                                'background-color': 'data(color)',
                                'label': 'data(label)',
                                'font-size': '12px',
                                'font-weight': 'bold',
                                'width': 30,
                                'height': 30
                            }
                        },
                        {
                            selector: 'edge',
                            style: {
                                'width': 'data(weight)',
                                'line-color': 'data(color)',
                                'target-arrow-color': 'data(color)',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'
                            }
                        },
                        {
                            selector: 'node[type="entry"]',
                            style: {
                                'width': 50,
                                'height': 50,
                                'font-size': '14px'
                            }
                        },
                        {
                            selector: 'node[type="mode"]',
                            style: {
                                'width': 40,
                                'height': 40,
                                'font-size': '13px'
                            }
                        }
                    ],
                    layout: {
                        name: 'cose',
                        animate: true,
                        animationDuration: 1000,
                        idealEdgeLength: 100,
                        nodeRepulsion: 400000
                    }
                });
            });
    </script>
</body>
</html>
```

## Visualization Recommendations

### For Documentation
- **Format:** PNG or PDF
- **Tool:** Graphviz with hierarchical layout
- **Resolution:** 300 DPI
- **Size:** Large format (A4 or larger)

### For Presentations
- **Format:** SVG or PNG
- **Tool:** Graphviz with force-directed layout
- **Resolution:** 150 DPI
- **Style:** Clean, color-coded sections

### For Interactive Exploration
- **Format:** HTML with JavaScript
- **Tool:** D3.js or Cytoscape.js
- **Features:** Zoom, pan, click for details, search

### For Web Embedding
- **Format:** SVG
- **Tool:** Graphviz or D3.js
- **Features:** Responsive, tooltips, click navigation

## Graph Structure

### Node Types
- **Entry** (gold): Main entry points (index, brands)
- **Mode** (4 colors): Primary navigation modes
- **Utility** (gray): Connect, links, privacy, terms
- **Content** (purple): Content hubs and pages
- **Interactive** (cyan): Interactive tools and games
- **About** (green): About and informational pages
- **Business** (yellow): Business-related pages
- **Music** (pink): Music projects and playlists
- **Series** (orange): Series and episodes
- **Visualization** (blue): Visualizations
- **Prototype** (indigo): Prototypes and concepts
- **Blog** (light pink): Blog posts
- **External** (gray, dashed): External platforms

### Edge Types
- **Primary** (thick, colored): Main navigation
- **Secondary** (medium): Content links
- **External** (dashed, gray): External platform links

### Color Scheme
- Entry Points: #FFD700 (gold)
- Consume Mode: #8B5CF6 (purple)
- Interact Mode: #06B6D4 (cyan)
- Learn Mode: #10B981 (green)
- Business Mode: #F59E0B (orange)
- Utility Pages: #6B7280 (gray)
- External Links: #9CA3AF (light gray)

## Customization Tips

### Adjusting Graph Size
In DOT file, modify:
```
dpi=150;  // Increase for higher resolution
ranksep=2.0;  // Increase spacing between levels
nodesep=1.0;  // Increase spacing between nodes
```

### Filtering by Type
Edit JSON or DOT file to show only specific node types (e.g., only modes, only content pages).

### Highlighting Paths
Add additional edges in DOT with different colors to highlight specific user journeys.

### Adding Labels
Add `label` attributes to edges in DOT file to show link types (nav, card, footer, etc.).

## Troubleshooting

### Graph too large or cluttered
- Use hierarchical layout instead of force-directed
- Filter nodes by type or category
- Increase canvas size and DPI
- Focus on specific sections by creating subgraphs

### Nodes overlapping
- Increase `ranksep` and `nodesep` values
- Use force-directed layout instead of hierarchical
- Increase canvas size
- Reduce node count by filtering

### Export quality issues
- Increase DPI setting
- Use SVG format for infinite scaling
- Generate PDF for print quality
- Use high-resolution PNG (300+ DPI)

## Next Steps

1. **Generate visualizations** using one of the methods above
2. **Analyze the graph** for navigation patterns and potential improvements
3. **Identify orphan pages** with few incoming links
4. **Find cross-linking opportunities** between sections
5. **Optimize user journeys** by analyzing paths through the graph
6. **Update the inventory** as the website evolves

## Contact

For questions or issues with the navigation inventory, refer to the main documentation in `NAVIGATION_INVENTORY.md`.

---

*Generated: January 31, 2026*
*Total Pages: 70+*
*Total Navigation Links: 400+*
