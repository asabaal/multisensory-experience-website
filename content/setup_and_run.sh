#!/bin/bash

echo "🤖 Setting up Agentic Blog Post Processor"

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Please set your ANTHROPIC_API_KEY environment variable"
    echo "   export ANTHROPIC_API_KEY='your-api-key-here'"
    exit 1
fi

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Make the script executable
chmod +x process_blog_posts.py

echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  Process all files:     python process_blog_posts.py"
echo "  Process specific file: python process_blog_posts.py filename.md"
echo ""
echo "🚀 Ready to generate blog posts with AI magic!"