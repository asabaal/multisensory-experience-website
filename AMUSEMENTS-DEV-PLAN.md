# Asabaal's Amusements - Development Plan

## Overview
Transforming "Blog 2.0" into "Asabaal's Amusements" - a multisensory experience platform hosting three main shows:
1. **Demos/Previews** - Existing 26 blog posts
2. **Life is your Word** - Reality series with Season 0 (15 episodes) and Season 1 (coming soon)
3. **Musical Poetry with Asabaal** - Inaugural Season 1 starting with one episode

---

## Phase 1: Main Hub - Asabaal's Amusements

### 1.1 Create New Hub Page
- `/amusements.html` - Main hub with 3 equal cards in grid
  - Demos/Previews card → links to blog listing
  - Life is your Word card → links to show page
  - Musical Poetry with Asabaal card → links to show page
- Design: Hero section with logo placeholder + title, then 3-card grid
- Match existing blog.html styling for consistency

### 1.2 Transform blog.html
- Update `/blog.html` to redirect to `/amusements.html`
- OR rebrand blog.html as "Asabaal's Amusements" and serve as hub
- Update navigation links across site to point to `/amusements.html`

### 1.3 Update Main Navigation
- Add "Amusements" to main navigation
- Update in `index.html` and other key pages
- Link to `/amusements.html`

---

## Phase 2: Asset Preparation

### 2.1 Create Show Assets Directory
```
/assets/shows/
├── amusements/
│   ├── logos/
│   │   └── asabaals-amusements-logo.png  [PLACEHOLDER]
│   └── banners/
│       └── amusements-banner.jpg
├── life-is-your-word/
│   ├── logos/
│   ├── banners/
│   ├── season-0/
│   │   ├── episode-1.jpg
│   │   └── ...
│   └── season-1/
│       └── coming-soon.jpg
└── musical-poetry/
    ├── logos/
    ├── banners/
    └── season-1/
        └── episode-1.jpg
```

### 2.2 Create Logo Placeholder
- Add placeholder at `/assets/shows/amusements/logos/asabaals-amusements-logo.png`
- Use text-based placeholder or simple graphic until actual logo is provided
- Document location for user to replace with real logo

---

## Phase 3: Life is Your Word - Structure

### 3.1 Create Show Overview Page
- `/life-is-your-word.html`
  - Show logo/banner
  - Show description (about show)
  - Season selector (Season 0, Season 1)
  - Season cards with status indicators
  - Quick stats (15 episodes in Season 0)

### 3.2 Create Season Pages
- `/life-is-your-word/season-0.html` (15 episodes)
  - Season title + description ("Pilot concept")
  - Episode grid with thumbnails
  - Episode numbers, titles, and descriptions
  - Season status: "Complete"
- `/life-is-your-word/season-1.html` (coming soon)
  - Season title + description
  - "Coming Soon" banner/visual
  - Release timeline teaser
  - Email signup notification form
  - Season status: "Coming Soon"

### 3.3 Create Episode Pages
- `/life-is-your-word/season-0/episode-1.html` through `/episode-15.html`
  - Show/season/episode breadcrumb navigation
  - Episode number and title
  - Video player or embed (YouTube/Vimeo/placeholder)
  - Episode description/content
  - Key quotes or takeaways
  - Previous/Next episode navigation
  - Back to Season button
  - Back to Show button

---

## Phase 4: Musical Poetry with Asabaal - Structure

### 4.1 Create Show Overview Page
- `/musical-poetry.html`
  - Show logo/banner
  - Show description (poetry + music concept)
  - Season display (Season 1)
  - Episode preview cards
  - Show-specific visual theme (more artistic/poetic)

### 4.2 Create Season Page
- `/musical-poetry/season-1.html`
  - Season description
  - Episode grid (starting with Episode 1)
  - Distinct visual design from Life is your Word
  - Episode count/status

### 4.3 Create Episode Pages
- `/musical-poetry/season-1/episode-1.html`
  - Breadcrumb navigation
  - Episode number and title
  - **Poem text display** (expandable/collapsible)
  - **Audio player** for spoken word/music
  - Episode artwork
  - Download options (audio, text, or both)
  - Previous/Next navigation
  - Back to buttons

---

## Phase 5: Data Structure & JavaScript

### 5.1 Create Shows Data File
- `/assets/js/amusements-data.js` - Central data structure with shows, seasons, episodes

### 5.2 Create Navigation Scripts
- `/assets/js/amusements-navigation.js`
  - Function to render 3-card grid from data
  - Season navigation logic
  - Episode navigation (prev/next with boundary checking)
  - Dynamic rendering of episode grids
  - Breadcrumb generation

---

## Phase 6: Blog Listing Page (Demos/Previews)

### 6.1 Create Blog Listing Page
- `/blog-listing.html` (or reuse existing blog.html for listing)
  - "Demos/Previews" header with description
  - Grid of all 26 existing blog posts
  - Can reuse existing blog post styling
  - Link back to Asabaal's Amusements

### 6.2 Preserve Existing Blog Posts
- Keep all 26 individual blog post pages intact
- Ensure they still work after transformation
- Update any internal links to point to new structure

---

## Phase 7: HTML Templates & Styling

### 7.1 Create Base Templates
- Template: `amusements-hub.html` - Main 3-card grid
- Template: `show-overview.html` - Show page with seasons
- Template: `season-overview.html` - Season page with episodes
- Template: `episode-page.html` - Episode content
- Template: `musical-poetry-episode.html` - Specialized for poetry episodes

### 7.2 Adapt Styling
- Reuse existing blog post CSS
- Add show-specific theme colors:
  - Demos/Previews: Purple theme (#8b5cf6)
  - Life is your Word: Gold/Orange theme (#fbbf24)
  - Musical Poetry: Cyan/Teal theme (#06b6d4)
- Create CSS classes for episode cards, season selectors, show logos/banners, video/audio players, breadcrumb navigation, Coming Soon banners

---

## Phase 8: Interactive Features

### 8.1 Show Navigation
- Season selector dropdown or tabs
- Episode grid with lazy loading
- Hover effects on episode cards
- Quick preview on hover (optional)

### 8.2 Episode Navigation
- Previous/Next buttons at top and bottom of episode
- Breadcrumb: Amusements → Show → Season → Episode
- Keyboard navigation (← → for episodes)

### 8.3 Coming Soon Features
- Email signup form for Season 1 notifications
- Countdown timer (optional)
- Social sharing for announcement

### 8.4 Musical Poetry Specific
- Custom audio player with progress
- Full-screen poem text mode
- Download audio/text options
- Background visualizer or artwork display
- Poem text scroll/expand functionality

---

## Phase 9: Content Population

### 9.1 Life is Your Word - Season 0
- Create placeholder content for 15 episodes (titles, descriptions, thumbnails, video embeds)

### 9.2 Musical Poetry - Season 1
- Create Episode 1 content (poem title, full poem text, audio file/embed, episode artwork, description)

### 9.3 Demo Content
- Ensure all 26 existing blog posts are accessible
- Verify thumbnail images exist
- Update any broken links

---

## Phase 10: Integration & Testing

### 10.1 Navigation Integration
- Add "Amusements" to main site navigation
- Test all cross-links between shows
- Verify breadcrumb navigation works
- Test prev/next episode buttons

### 10.2 Responsive Testing
- Mobile: Single column cards
- Tablet: 2-column grids
- Desktop: 3-column layouts
- Test audio/video players on mobile

### 10.3 Performance
- Optimize image sizes
- Lazy load episode grids
- Minify JavaScript
- Cache static assets

### 10.4 Accessibility
- Alt text for all images
- Keyboard navigation
- Screen reader friendly
- ARIA labels for audio/video

---

## Deliverables Summary

### New Files to Create:
- `/amusements.html` (1 file - main hub)
- `/life-is-your-word.html` (1 file)
- `/life-is-your-word/season-0.html` (1 file)
- `/life-is-your-word/season-1.html` (1 file)
- `/life-is-your-word/season-0/episode-1.html` through `episode-15.html` (15 files)
- `/musical-poetry.html` (1 file)
- `/musical-poetry/season-1.html` (1 file)
- `/musical-poetry/season-1/episode-1.html` (1 file)
- `/blog-listing.html` (1 file - or transform existing)
- `/assets/js/amusements-data.js` (1 file)
- `/assets/js/amusements-navigation.js` (1 file)

### Files to Modify:
- `/index.html` - Add Amusements to navigation
- `/blog.html` - Transform to redirect or rebrand
- `/assets/js/blog-data.js` - May need updates

### Directories to Create:
- `/assets/shows/amusements/logos/` + `banners/`
- `/assets/shows/life-is-your-word/logos/` + `banners/` + `season-0/` + `season-1/`
- `/assets/shows/musical-poetry/logos/` + `banners/` + `season-1/`

### Assets Needed (with placeholders):
- Asabaal's Amusements logo (placeholder)
- Life is your Word logo/banner
- Musical Poetry logo/banner
- 15 Life is your Word episode thumbnails
- 1 Musical Poetry episode artwork
- Season 1 "Coming Soon" graphic

---

## Estimated Effort
- **Frontend Development**: 10-14 hours
- **Content Population**: 6-8 hours
- **Testing & Polish**: 3-5 hours
- **Total**: 19-27 hours
