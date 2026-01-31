# Asabaal's Amusements - Asset Structure

## Overview
This directory contains all visual assets for Asabaal's Amusements platform, including logos, banners, and episode thumbnails.

## Directory Structure

```
assets/shows/
├── amusements/
│   ├── logos/
│   │   └── asabaals-amusements-logo.png [PLACEHOLDER]
│   └── banners/
│       ├── amusements-banner.jpg [PLACEHOLDER]
│       └── demos-preview.jpg [PLACEHOLDER]
├── life-is-your-word/
│   ├── logos/
│   │   └── logo.png [PLACEHOLDER]
│   ├── banners/
│   │   ├── banner.jpg [PLACEHOLDER]
│   │   └── coming-soon.jpg [PLACEHOLDER]
│   ├── season-0/
│   │   ├── episode-1.jpg [PLACEHOLDER]
│   │   ├── episode-2.jpg [PLACEHOLDER]
│   │   └── ... [episodes 3-15]
│   └── season-1/
│       └── coming-soon.jpg [PLACEHOLDER]
└── musical-poetry/
    ├── logos/
    │   └── logo.png [PLACEHOLDER]
    ├── banners/
    │   └── banner.jpg [PLACEHOLDER]
    └── season-1/
        └── episode-1.jpg [PLACEHOLDER]
```

## Asset Specifications

### Image Dimensions
- **Show Logos**: 500x500px (square or slightly rectangular)
- **Show Banners**: 1920x1080px (16:9 aspect ratio)
- **Episode Thumbnails**: 1280x720px (16:9 aspect ratio)

### File Formats
- PNG for logos (transparency)
- JPG for banners and thumbnails (optimized for web)

### Color Themes
- **Amusements**: Gold/Orange (#fbbf24, #f472b6)
- **Demos/Previews**: Purple/Cyan (#8b5cf6, #06b6d4)
- **Life is your Word**: Gold/Pink (#fbbf24, #f472b6)
- **Musical Poetry**: Cyan/Teal (#06b6d4, #10b981)

## Asset Status

### Completed
- ✅ Directory structure created
- ✅ Placeholder styling implemented
- ✅ Responsive design implemented
- ✅ Color themes applied

### Needed (Placeholders)
- ⏳ Asabaal's Amusements logo (user has logo)
- ⏳ Life is your Word logo
- ⏳ Life is your Word banner
- ⏳ Musical Poetry logo
- ⏳ Musical Poetry banner
- ⏳ 15 Life is your Word episode thumbnails
- ⏳ 1 Musical Poetry episode artwork
- ⏳ Season 1 "Coming Soon" graphics

## Implementation Notes

### Current Implementation
- All pages use gradient backgrounds and emojis/text as placeholders
- When real assets are available, simply replace placeholder files
- Update HTML to use actual image files instead of gradients

### To Add Real Assets
1. Place image files in corresponding directories
2. Update HTML references:
   - Replace `style="background: gradient..."` with `<img src="...">`
   - Update `src` attributes for logos and thumbnails
3. Test across all page types:
   - Amusements hub
   - Show overview pages
   - Season pages
   - Episode pages

## Next Steps
1. [ ] Add real show logos
2. [ ] Add show banners
3. [ ] Add episode thumbnails
4. [ ] Add "Coming Soon" graphics
5. [ ] Optimize images for web (WebP format recommended)
6. [ ] Add alt text for accessibility
