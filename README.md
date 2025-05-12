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
- A simple local server (optional, for testing)

### Running Locally

1. Clone this repository:
   ```
   git clone https://github.com/asabaal/multisensory-experience-website.git
   ```

2. Navigate to the project directory:
   ```
   cd multisensory-experience-website
   ```

3. Open `index.html` in your browser directly, or for better results, serve the files using a local development server:

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

### Making Changes

1. Edit the HTML, CSS, or JavaScript files as needed
2. Refresh your browser to see changes (Live Server will do this automatically)
3. Commit your changes using Git if desired

## Deployment to Production

### Server Requirements

- Any web server that can serve static files (Apache, Nginx, etc.)
- HTTPS support recommended for security

### Deployment Steps

1. **Using SFTP/FTP:**
   - Upload all files to your web server's public directory
   - Ensure file permissions are set correctly

2. **Using Git (if your server supports it):**
   ```
   git clone https://github.com/asabaal/multisensory-experience-website.git
   ```

3. **Using a Virtual Machine:**
   - Install a web server (Nginx recommended)
   - Configure the server to point to your website directory
   - Set up proper permissions and security

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /path/to/multisensory-experience-website;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # Add caching for static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }
}
```

## Future Development

- Add dynamic functionality through backend integration
- Implement database for blog posts and events
- Create fully interactive elements for the Imagination page
- Add user authentication for community features
- Implement custom CMS for easier content updates

## License

This project is proprietary and confidential. All rights reserved.

## Contact

For questions or support, please contact [your contact information].
