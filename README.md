# Multisensory Experience Website

A modern, responsive website for a business focused on creating multisensory experiences in a post-labor economy. The site showcases our vision, content, and future plans for building community spaces that foster personal growth and societal betterment.

## Project Overview

This website serves as both a representation of our current business phase (Digital Foundation) and a vision of where we're heading. We're currently using AI to create content and software, with plans to develop algorithmic trading for self-funding and eventually build physical community centers.

### Key Features

- Modern, futuristic design reflecting our innovative approach
- Responsive layout for all device sizes
- Multiple content sections showcasing our multisensory experiences
- Blog and news sections for thought leadership
- Interactive elements on the Imagination page
- Roadmap visualization of our business evolution
- Contact forms and newsletter signups

## Technology Stack

- HTML5 for semantic markup
- CSS3 with custom properties (variables) for styling
- Vanilla JavaScript for interactive elements
- SVG for icons and illustrations
- No external libraries or frameworks for better performance
- Custom animations and transitions
- Mobile-first responsive design

## Project Structure

```
multisensory-experience-website/
├── css/                        # CSS files
│   ├── components/             # Component-specific styles
│   │   ├── buttons.css
│   │   ├── cards.css
│   │   ├── footer.css
│   │   ├── forms.css
│   │   └── header.css
│   ├── pages/                  # Page-specific styles
│   │   ├── home.css
│   │   ├── blog.css
│   │   └── ...
│   ├── main.css                # Main stylesheet (imports all others)
│   ├── reset.css               # CSS reset
│   └── variables.css           # CSS custom properties
├── js/                         # JavaScript files
│   ├── pages/                  # Page-specific scripts
│   │   ├── blog.js
│   │   └── ...
│   └── main.js                 # Main JavaScript file
├── images/                     # Image assets
│   ├── logo.svg
│   ├── logo-white.svg
│   └── ...
├── templates/                  # HTML templates
│   └── template.html           # Base template for all pages
├── index.html                  # Home page
├── blog.html                   # Blog page
├── news.html                   # News page
├── featured.html               # Featured content page
├── events.html                 # Events page
├── approach.html               # Our Evolving Approach page
├── invest.html                 # Investment Opportunities page
├── community.html              # Community Center Concept page
├── imagination.html            # Imagination page
├── CLAUDE.md                   # Guidelines for Claude Code AI
└── README.md                   # Project documentation
```

## Pages

1. **Home** - Overview and introduction to our vision
2. **Blog** - Thought leadership and insights
3. **News** - Current events through our unique lens
4. **Featured Content** - Showcase of our multisensory experiences
5. **Events** - Calendar of virtual and future physical gatherings
6. **Our Evolving Approach** - Business model and roadmap
7. **Investment Opportunities** - Funding and partnership options
8. **Community Center Concept** - Vision for physical spaces
9. **Imagination** - Interactive experience demonstrating our approach

## Local Development Setup

### Prerequisites

- A modern web browser (Chrome, Firefox, Edge, Safari)
- Basic knowledge of HTML, CSS, and JavaScript (for modifications)
- Git (optional, for version control)
- A simple local server (required for proper path resolution)

### Running Locally

1. Clone this repository:
   ```
   git clone https://github.com/asabaal/multisensory-experience-website.git
   ```

2. Navigate to the project directory:
   ```
   cd multisensory-experience-website
   ```

3. Serve the files using a local development server:

   **Using VS Code:**
   - Install the "Live Server" extension
   - Right-click on index.html and select "Open with Live Server"

   **Using Node.js (if installed):**
   ```
   npx http-server
   ```
   Then visit http://localhost:8080 in your browser

   **Using Python (if installed):**
   ```
   # Python 3
   python -m http.server
   # Python 2
   python -m SimpleHTTPServer
   ```
   Then visit http://localhost:8000 in your browser

   > **Note:** Opening the HTML files directly in your browser may not work properly due to the absolute paths used in the code. A local server is recommended.

### Making Changes

1. Edit the HTML, CSS, or JavaScript files as needed
2. Refresh your browser to see changes (Live Server will do this automatically)
3. Follow the established code conventions:
   - Use 2-space indentation
   - Follow BEM naming for CSS classes
   - Keep JavaScript functions small and focused
   - Add appropriate comments for complex logic

## Deployment to Production

### Server Requirements

- Any web server that can serve static files (Apache, Nginx, etc.)
- HTTPS support recommended for security

### Deployment Steps

1. **Using SFTP/FTP:**
   - Upload all files to your web server's public directory
   - Ensure file permissions are set correctly (typically 644 for files, 755 for directories)

2. **Using Git (if your server supports it):**
   ```
   git clone https://github.com/asabaal/multisensory-experience-website.git
   ```

3. **Using a Virtual Machine (such as Abacus AI):**
   - Install a web server (Nginx recommended)
   - Configure the server to point to your website directory
   - Set up proper permissions and security

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificate configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Website root directory
    root /path/to/multisensory-experience-website;
    index index.html;

    # Default location block
    location / {
        try_files $uri $uri/ =404;
    }

    # Add caching for static assets
    location ~* \.(jpg|jpeg|png|gif|ico|svg|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Compression for text files
    gzip on;
    gzip_types text/plain text/css application/javascript application/json;
}
```

## Performance Optimization

The website has been optimized for performance in several ways:

1. **Minimal Dependencies** - No external JavaScript or CSS libraries
2. **Optimized Assets** - SVG images for icons and logo
3. **CSS Organization** - Modular CSS with specific component files
4. **Responsive Images** - Ensuring images are appropriately sized
5. **Caching Strategy** - Recommended server caching for static assets
6. **Code Splitting** - Page-specific CSS and JavaScript files
7. **Animations** - CSS transitions for smoother animations
8. **System Fonts** - Using system font stack for better performance

## Future Development

- Add dynamic functionality through backend integration
- Implement database for blog posts and events
- Create fully interactive elements for the Imagination page
- Add user authentication for community features
- Implement custom CMS for easier content updates
- Add internationalization (i18n) support
- Implement more advanced animations and interactive elements

## Browser Support

The website is designed to work on modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- iOS Safari and Android Chrome for mobile devices

## License

This project is proprietary and confidential. All rights reserved.

## Contact

For questions or support, please contact [your contact information]
