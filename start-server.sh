#!/bin/bash

# Simple script to start a local server for testing the blog
echo "Starting local server for Multisensory Blog..."
echo "Navigate to http://localhost:8000 to view the site"
echo "Visit http://localhost:8000/blog.html to see the blog"
echo ""
echo "Press Ctrl+C to stop the server"

# Start Python HTTP server
python3 -m http.server 8000