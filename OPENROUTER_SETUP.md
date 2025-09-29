# OpenRouter Qwen3 Coder Setup Guide

This guide explains how to set up and use the OpenRouter backend with Qwen3 Coder model for automated blog processing.

## 🚀 Quick Start

### 1. Get OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key

### 2. Set Environment Variable

```bash
export OPENROUTER_API_KEY='sk-or-your-api-key-here'
```

### 3. Test Connection

```bash
python test_openrouter_connection.py
```

### 4. Process Blog Posts

```bash
# Process all markdown files
python content/openrouter_qwen3_processor.py

# Process specific file
python content/openrouter_qwen3_processor.py --file content/raw-input/your-post.md

# With verbose output
python content/openrouter_qwen3_processor.py --verbose
```

## 📁 File Structure

```
content/
├── raw-input/              # Place markdown files here
│   ├── post1.md
│   └── post2.md
├── blog/published/         # Generated JSON files appear here
│   ├── 2024-12-01_post1/
│   │   └── post.json
│   └── 2024-12-02_post2/
│       └── post.json
├── templates/
│   └── post-template.json  # Template structure
└── openrouter_qwen3_processor.py  # Main processor
```

## 📝 Input Format

Place your markdown blog posts in `content/raw-input/`. The processor will:

1. Extract title, content, and metadata
2. Generate appropriate tags and excerpt
3. Create structured JSON following the template
4. Save to `content/blog/published/` with date-based directory

### Example Markdown Input

```markdown
# Your Blog Post Title

This is the introduction to your blog post. It should be engaging and informative.

## Section 1

Content for your first section goes here. You can use **bold**, *italic*, and other markdown formatting.

## Section 2

More content here. The processor will preserve all markdown formatting in the final JSON.
```

## 🤖 Model Configuration

The processor uses **Qwen3 Coder 32B Instruct** model:

- **Model**: `qwen/qwen-2.5-coder-32b-instruct`
- **Max Tokens**: 6000 (for blog processing)
- **Temperature**: 0.3 (balanced creativity/consistency)
- **API**: OpenRouter

## 🔧 Configuration Options

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your-openrouter-api-key

# Optional (for alternative processing)
CLAUDE_CODE_OAUTH_TOKEN=your-claude-oauth-token
```

### Command Line Options

```bash
python content/openrouter_qwen3_processor.py [OPTIONS]

Options:
  --verbose, -v          Show detailed timing information
  --auto-update, -a      Auto-update existing posts
  --file, -f FILE        Process specific file only
  --help, -h            Show help message
```

## 🎯 Features

### ✅ What Qwen3 Coder Does

- **Markdown to JSON Conversion**: Converts markdown posts to structured JSON
- **Metadata Extraction**: Automatically generates titles, slugs, tags, excerpts
- **Content Structuring**: Organizes content into sections with proper formatting
- **Template Compliance**: Ensures all required fields are present
- **Validation**: Checks JSON validity and required fields

### 🔄 Processing Pipeline

1. **Input**: Markdown file from `raw-input/`
2. **Analysis**: Qwen3 analyzes content and structure
3. **Generation**: Creates structured JSON with metadata
4. **Validation**: Checks for completeness and validity
5. **Output**: Saves to dated directory in `blog/published/`

## 🛠️ Troubleshooting

### Common Issues

**API Key Not Found**
```
❌ OPENROUTER_API_KEY environment variable not set!
```
**Solution**: Set the environment variable:
```bash
export OPENROUTER_API_KEY='your-api-key-here'
```

**Connection Failed**
```
❌ API call failed: 401 Unauthorized
```
**Solution**: Check your API key and ensure it's valid.

**JSON Parsing Error**
```
❌ JSON parsing error for file.md: Expecting value: line 1 column 1
```
**Solution**: The model response wasn't valid JSON. This can happen with complex content. Try simplifying the input or check the raw response.

**Template Missing**
```
❌ Template not found: content/templates/post-template.json
```
**Solution**: Ensure the template file exists in the correct location.

### Debug Mode

Use verbose mode to see detailed processing information:
```bash
python content/openrouter_qwen3_processor.py --verbose
```

## 📊 Performance

- **Processing Time**: ~10-30 seconds per post (depends on content length)
- **API Cost**: Varies based on content length and model usage
- **Success Rate**: High for well-structured markdown content

## 🔄 Migration from Claude

If you're migrating from the Claude-based processor:

1. **Same Input Format**: No changes needed to your markdown files
2. **Same Output Format**: JSON structure remains identical
3. **Environment Variables**: Add `OPENROUTER_API_KEY` instead of `CLAUDE_CODE_OAUTH_TOKEN`
4. **Command Structure**: Same command-line options and usage patterns

## 🎉 Next Steps

1. **Test Connection**: Run `python test_openrouter_connection.py`
2. **Process Sample**: Try with a single markdown file
3. **Batch Process**: Process all files in `raw-input/`
4. **Review Output**: Check generated JSON files in `blog/published/`
5. **Integrate**: Use the processor in your blog workflow

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your OpenRouter API key is valid
3. Ensure network connectivity to OpenRouter API
4. Review the verbose output for detailed error information

For feature requests or bug reports, please create an issue in the repository.