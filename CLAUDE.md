# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands
- Local server: `npx http-server` or `python -m http.server`
- Open in browser: http://localhost:8080 (Node.js) or http://localhost:8000 (Python)
- VS Code users: Use "Live Server" extension to preview changes in real-time

## Code Style Guidelines
- HTML: Semantic markup with proper indentation (2 spaces)
- CSS: Follow BEM naming convention for classes; use variables for colors/sizes
- JavaScript: ES6+ syntax, avoid jQuery unless necessary
- Responsive design: Mobile-first approach with appropriate breakpoints
- Error handling: Graceful degradation for JS features
- Performance: Optimize images, minimize HTTP requests, leverage browser caching
- Accessibility: Ensure WCAG 2.1 AA compliance (proper contrast, alt text, ARIA)
- Keep file sizes small and load times fast (especially for images and scripts)

## Project Structure
- Maintain separation of concerns (HTML structure, CSS presentation, JS behavior)
- Organize assets in subdirectories (/css, /js, /images, /fonts)
- Follow RESTful principles for any future API integrations