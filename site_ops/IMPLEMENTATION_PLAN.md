# Visual Website Maintenance Database - Implementation Plan

## 📊 Project Overview

**Objective:** Create an interactive web-based maintenance database system for 78 website pages

**Data Source:** `site_maintenance_log.csv` (78 pages, 17 columns)
**Assets:** `site_ops/screenshots/` (78 PNG files)
**Technology Stack:** Vanilla JavaScript + CSS (no frameworks, data-agnostic)
**Implementation Location:** `site_ops/` directory

---

## 🎯 File Structure

```
site_ops/
├── maintenance-db/
│   ├── index.html (NEW - Main application)
│   ├── css/
│   │   └── maintenance-db.css (NEW - Styles)
│   └── js/
│       ├── maintenance-db.js (NEW - Application logic)
│       └── papaparse.min.js (LIBRARY - CSV parsing)
├── screenshots/
│   ├── index.png
│   ├── amusements.png
│   ├── blog/post-asabaal-ventures-dawn-new-era.png
│   └── ... (78 PNG files total)
```

---

## 📋 Task List

### Phase 1: File Structure Setup
- [ ] Create `maintenance-db/` directory
- [ ] Create `css/maintenance-db.css` stylesheet
- [ ] Create `js/maintenance-db.js` application logic
- [ ] Download PapaParse.min.js library to `/js/`
- [ ] Verify all paths exist

### Phase 2: HTML Structure
- [ ] Create `index.html` with proper HTML5 boilerplate
- [ ] Add viewport meta tag for responsiveness
- [ ] Include PapaParse.min.js library from CDN
- [ ] Load maintenance-db.js application script
- [ ] Create split-view layout structure

### Phase 3: CSS Styling
- [ ] Define CSS variables for site color scheme (purple gradient theme)
- [ ] Create container with max-width and centering
- [ ] Implement split-view grid layout (70% table, 30% details panel)
- [ ] Style filter section (dropdowns, search input)
- [ ] Create table styles (sticky headers, hover effects, row colors)
- [ ] Create details panel styles (fixed positioning, hidden state)
- [ ] Add responsive breakpoints (desktop, tablet, mobile)

### Phase 4: JavaScript Core Functionality
- [ ] Create state management object:
  - [ ] `allRows` - all 78 pages
  - [ ] `filteredRows` - currently filtered pages
  - [ ] `selectedRow` - currently selected page
  - [ ] `filters` - current filter values
- [ ] Implement CSV parsing with PapaParse
- [ ] Load `site_maintenance_log.csv` on page load
- [ ] Handle CSV parsing errors with user notification
- [ ] Initialize application on DOMContentLoaded

### Phase 5: Table Rendering
- [ ] Create table container element
- [ ] Implement `renderTable()` function:
  - [ ] Create table header row with column names
  - [ ] Implement `renderRow()` function for single page
  - [ ] Map CSV columns to table cells:
    - [ ] Page Type (filterable, badge)
    - [ ] Page Title (sortable)
    - [ ] Inbound/Outbound Links (numeric, sortable)
    - [ ] Mobile Responsive (Yes/No with color coding)
    - [ ] Issues (badge with count)
- [ ] Create table body element
- [ ] Add click event listeners to rows
- [ ] Implement `sortTable()` function for column sorting
- [ ] Add row selection highlighting
- [ ] Implement filter functionality with `applyFilters()`

### Phase 6: Filtering System
- [ ] Create filter UI controls:
  - [ ] Page Type dropdown (Content Hub, Blog Post, etc.)
  - [ ] Search input for Page URL/Title
  - [ ] Mobile Responsive dropdown (All, Yes, No)
  - [ ] Issues filter (Has Issues, No Issues)
- [ ] Implement `applyFilters()` function:
    - [ ] Filter by Page Type
    - [ ] Filter by Mobile Responsive status
    - [ ] Filter by issue presence
    - [ ] Search by text in Page URL or Title
  - [ ] Re-render table with filtered results
    - [ ] Update filter count display
- [ ] Implement clear filters button to reset all filters

### Phase 7: Details Panel
- [ ] Create details panel HTML structure:
  - [ ] Screenshot preview section (large image)
  - [ ] Detected Issues section (expandable bullet list)
  - [ ] Page Metadata section
  - [ ] Template Used
  - [ ] Inbound Links
  - [ ] Outbound Links
  - [ ] Last Reviewed Date
- [ ] Implement `showDetails()` function:
    - [ ] Build screenshot path: `/site_ops/screenshots/{converted_filename}`
    - [ ] Load screenshot with error handling
    - [ ] Parse issues string into array (split by semicolon)
    - [ ] Display issues as bullet points
    - [ ] Add "no issues" message if empty
- [ ] Add close button functionality (hide panel, deselect row)
- [ ] Implement expand/collapse toggle for issues

### Phase 8: Screenshot Handling
- [ ] Implement `convertPageToFilename()` function:
  - [ ] Remove .html extension
  - [ ] Replace `/` with `_` (multiple times)
  - [ ] Add .png extension
  - [ ] Examples:
    - [ ] `index.html` → `index.png`
    - [ ] `blog/post-xxx.html` → `blog_post_xxx.png`
    - [ ] `musical-poetry/season-1/episode-1.html` → `musical_poetry_season_1_episode_1.png`
- [ ] Implement `getScreenshotPath()` function
- [ ] Implement image load error handling (onerror event)
- [ ] Display placeholder image on load error

### Phase 9: Event Handlers
- [ ] Add click event to table rows:
  - [ ] Highlight selected row
  - [ ] Call `showDetails()` for selected page
- [ ] Remove highlight from previous selection
- [ ] Add close button event to details panel
- [ ] Add filter change events (dropdowns, search input)
- [ ] Add window resize event (for responsive layout)
- [ ] Implement event delegation pattern for performance
- [ ] Add escape key handler (close details panel)

### Phase 10: Responsive Design
- [ ] Create media query breakpoints:
  - [ ] Desktop: > 1200px - split view
  - [ ] Tablet: 768px - 1200px - stack view
  - [ ] Mobile: < 768px - modal view
- [ ] Implement responsive CSS rules:
  - [ ] Grid layout changes based on breakpoint
  - [ ] Details panel positioning changes
  - [ ] Table column hiding on mobile
  - [ ] Font size adjustments
- [ ] Add mobile menu button (visible on mobile only)

### Phase 11: Color Scheme Implementation
- [ ] Define CSS custom properties:
  - [ ] `--bg-primary` - #0f0f23
  - [ ] `--bg-secondary` - #1a1a3e
  - [ ] `--accent-gold` - #fbbf24
  - [ ] `--accent-pink` - #f472b6
- [ ] `--accent-purple` - #8b5cf6
- [ ] `--text-primary` - #e5e7eb
  - [ ] `--text-secondary` - #9ca3af
- [ ] `--border-color` - #2d1b69
  - [ ] `--success-green` - #10b981
- [ ] `--danger-red` - #ef4444
- [ ] Implement gradient backgrounds using color variables
- [ ] Apply colors to headers, buttons, badges
- [ ] Ensure sufficient contrast for accessibility

### Phase 12: Data Agnostic Verification
- [ ] Verify application works without any backend dependencies
- [ ] Test CSV loading (parse site_maintenance_log.csv)
- [ ] Test screenshot loading (load from `/site_ops/screenshots/`)
- [ ] Verify no database or API calls
- [ ] Confirm data flows: CSV → JS State → DOM Display
- [ ] Test with different CSV files to ensure data-agnostic

### Phase 13: Performance Optimization
- [ ] Implement virtual scrolling for large datasets (if needed)
- [ ] Use event delegation for table events
- [ ] Lazy load screenshots on demand (don't load all 78 at once)
- [ ] Debounce search input (wait 300ms after user stops typing)
- [ ] Use CSS transitions instead of animations
- [ ] Minimize DOM manipulation (batch updates)

### Phase 14: Accessibility Features
- [ ] Add ARIA labels to interactive elements
- [ ] Ensure keyboard navigation support (tab to filters, tab to rows)
- [ ] Add focus indicators for selected elements
- [ ] Use semantic HTML elements (table, thead, tbody, button)
- [ ] Ensure sufficient color contrast (WCAG AA standards)
- [ ] Add skip to main content links (for screen readers)

### Phase 15: Error Handling & User Feedback
- [ ] Add loading state during CSV parsing
- [ ] Add error message display if CSV fails to load
- [ ] Add "no pages found" state if filter returns empty results
- [ ] Add console error logging for debugging
- [ ] Add user-friendly error messages
- [ ] Implement error boundary for JavaScript errors

### Phase 16: Testing & Validation
- [ ] Test with all 78 pages loaded in CSV
- [ ] Verify all screenshots display correctly
- [ ] Test filters work correctly
- [ ] Test sorting on all sortable columns
- [ ] Test row selection and details panel
- [ ] Test responsive behavior at different viewport sizes
- [ ] Verify CSV updates persist (manually check if needed)
- [ ] Test browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Performance test (load time, interactions)
- [ ] Accessibility tested with screen reader

### Phase 17: Documentation
- [ ] Add inline code comments for key functions
- [ ] Create user guide (simple README)
- [ ] Document keyboard shortcuts
- [ ] Document CSV column mapping
- [ ] Document file structure and dependencies
- [ ] Add troubleshooting guide for common issues

---

## 🚀 Implementation Order

### Sprint 1: Foundation (Tasks 1-5)
**Priority:** HIGH - Required for all features
**Dependencies:** None
**Estimated Time:** 2 hours

### Sprint 2: Core Features (Tasks 6-10)
**Priority:** HIGH - Required for basic functionality
**Dependencies:** PapaParse library
**Estimated Time:** 3 hours

### Sprint 3: Interactive Features (Tasks 11-12)
**Priority:** MEDIUM - Enhances user experience
**Dependencies:** Sprint 2
**Estimated Time:** 2 hours

### Sprint 4: Screenshots (Tasks 13-14)
**Priority:** MEDIUM - Visual component
**Dependencies:** Sprint 2
**Estimated Time:** 1 hour

### Sprint 5: Responsive Design (Tasks 15)
**Priority:** MEDIUM - Required for mobile users
**Dependencies:** Sprint 2
**Estimated Time:** 2 hours

### Sprint 6: Color Scheme (Tasks 16)
**Priority:** MEDIUM - Brand consistency
**Dependencies:** Sprint 1
**Estimated Time:** 30 minutes

### Sprint 7: Optimization (Tasks 17)
**Priority:** LOW - Performance enhancement
**Dependencies:** Sprint 6
**Estimated Time:** 1 hour

### Sprint 8: Testing & Documentation (Tasks 18-20)
**Priority:** LOW - Quality assurance
**Dependencies:** All sprints
**Estimated Time:** 2 hours

**Total Estimated Time:** 13.5 hours

---

## 📊 Success Criteria

### Functional Requirements
- [ ] CSV loads successfully with all 78 pages
- [ ] Table displays all 78 pages correctly
- [ ] Filters work (Page Type, Mobile Responsive, Issues)
- [ ] Search functionality works
- [ ] Clicking row shows details panel
- [ ] Details panel displays correct screenshot
- [ ] Details panel shows all detected issues
- [ ] Issues column shows count badge
- [ ] Close button hides details panel
- [ ] All 78 screenshots are accessible
- [ ] Responsive layout works on desktop, tablet, mobile
- [ ] No JavaScript errors in console

### Performance Requirements
- [ ] Page loads in < 2 seconds
- [ ] Filters apply instantly (< 100ms)
- [ ] Row selection is instant
- [ ] Details panel appears instantly (< 100ms)
- [ ] Screenshot loads on demand (not preloaded)
- [ ] Scrolling is smooth at 60fps

### Accessibility Requirements
- [ ] All interactive elements have ARIA labels
- [ ] Keyboard navigation works (tab to filters, tab to rows)
- [ ] Focus indicators are visible
- [ ] Color contrast is sufficient (WCAG AA)
- [ ] Screen reader compatible

### Code Quality Requirements
- [ ] Code is well-commented
- [ ] Functions have single responsibility
- [ ] No code duplication
- [ ] Error handling is comprehensive
- [ ] Follows DRY principle

---

## 🎯 Key Design Decisions

### Why Vanilla JS + CSS?
- **Data Agnostic:** Works with any CSV structure, no backend assumptions
- **Fast:** No framework overhead, instant loading
- **Portable:** Can be opened directly in browser without server
- **Simple:** Easy to understand and maintain
- **No Build Step:** HTML file is a build artifact

### Why Split View?
- **Efficient:** See more data at once (table + details side-by-side)
- **Comparison:** Easy to compare issues across pages
- **Workflow:** Filter → Select Row → Review Details → Next Row

### Why PapaParse?
- **Fast:** Optimized CSV parser
- **Small:** Minified version is 50KB
- **Reliable:** Handles edge cases (quotes, special characters)
- **Easy:** Simple API, no complex configuration

---

## 🚨 Risks & Mitigations

### Risk 1: File path issues for screenshots
**Mitigation:** Implement robust filename conversion, test with nested paths

### Risk 2: Large CSV performance
**Mitigation:** Implement pagination or virtual scrolling if needed

### Risk 3: Mobile display of large table
**Mitigation:** Stack details panel below table on mobile, keep table full width

### Risk 4: Browser compatibility
**Mitigation:** Use standard HTML5/CSS3 features, avoid experimental APIs

---

## 📈 Milestones

### Week 1: Foundation
- [ ] File structure complete
- [ ] HTML/CSS/JS files created
- [ ] PapaParse integrated
- [ ] Basic table rendering works
- [ ] CSV loading works

### Week 2: Core Features
- [ ] Filtering system complete
- [ ] Search functionality works
- [ ] Row selection works
- [ ] Details panel displays screenshots
- [ ] Issues display working

### Week 2: Polish & Optimization
- [ ] Responsive design complete
- [ ] Color scheme applied
- [ ] Performance optimized
- [ ] Accessibility features added
- [ ] Cross-browser testing complete

### Week 2: Documentation & Delivery
- [ ] User guide created
- [ ] Code comments complete
- [ ] All tests passing
- [ ] Ready for production use

---

## 📁 File Structure After Implementation

```
/mnt/storage/repos/multisensory-experience-website/site_ops/
├── maintenance-db/
│   ├── index.html (NEW - Main application)
│   ├── css/
│   │   └── maintenance-db.css (NEW - Styles)
│   └── js/
│       ├── maintenance-db.js (NEW - Application logic)
│       └── papaparse.min.js (LIBRARY - CSV parsing)
├── screenshots/
│   ├── index.png
│   ├── amusements.png
│   ├── blog/post-asabaal-ventures-dawn-new-era.png
│   └── ... (78 PNG files total)
```

---

## 🔍 Dependencies & External Libraries

### Required
- **PapaParse** - CSV parsing library
  - CDN: `https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js`
  - Size: ~50KB minified
  - License: MIT
  - Purpose: Parse site_maintenance_log.csv

### No Other Dependencies
- ❌ No React/Vue/Angular
- ❌ No jQuery
- ❌ No Bootstrap/Tailwind
- ❌ No backend framework
- ❌ No build tools (Webpack/Vite)

---

## 🎨 UI Mockup / Wireframe

### Desktop Layout (>1200px)
```
┌─────────────────────────────────────────────────────────┐
│  🔍 Filters                      │  📊 Details Panel     │
│  [Page Type ▼]  [Search: ______]              │  │  ┌─────────────────────┐ │
│  │                                   │  │  │  📸 Screenshot      │  │
│  └─────────────────────────────────────────────────────────┘ │  └─────────────────────────────┴─┘ │
│                                                            │                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Maintenance Table (78 pages)             │  │                           │
│  │  Type  │ Title                    │ Links │ Issues │ Date  │
│  ├─────────────────────────────────────────────────────┤  │
│  │  Hub   │ Amusements                │ 7/8    │ 3      │ 2026-02-07  │
│  │  Hub   │ Blog Listing              │ 26/7   │ 0      │ 2026-02-07  │
│  │  │     │  ┌─────────────────────────────┤  │  │
│  │  Post   │ Electric Pulse            │ 0/7    │ 1      │ 2026-02-07  │
│  │  │     │ └─────────────────────────────┘ │  │
│  │  │     │                           │
│  ... (76 more rows)                    │                          │
│  └─────────────────────────────────────────────────────────────┘
```

### Mobile Layout (<768px)
```
┌───────────────────────────────────────────┐
│  🔍 Filters                              │
│  [Page Type ▼]                         │
│  [Search: ______]                      │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│  Maintenance Table (78 pages)             │
│  (Full width, horizontal scroll)         │
│  Type  │ Title │ Links │ Issues │ Date│
│  Hub   │ Amusements │ 7/8   │ 3    │ ... │
│  ... (76 more rows)                    │                          │
└─────────────────────────────────────────────────────────────┘

[Tap row to see details]
```

---

## 🚀 Implementation Order

### Sprint 1: Foundation (Tasks 1-5)
**Priority:** HIGH - Required for all features
**Dependencies:** None
**Estimated Time:** 2 hours

### Sprint 2: Core Features (Tasks 6-10)
**Priority:** HIGH - Required for basic functionality
**Dependencies:** PapaParse library
**Estimated Time:** 3 hours

### Sprint 3: Interactive Features (Tasks 11-12)
**Priority:** MEDIUM - Enhances user experience
**Dependencies:** Sprint 2
**Estimated Time:** 2 hours

### Sprint 4: Screenshots (Tasks 13-14)
**Priority:** MEDIUM - Visual component
**Dependencies:** Sprint 2
**Estimated Time:** 1 hour

### Sprint 5: Responsive Design (Tasks 15)
**Priority:** MEDIUM - Required for mobile users
**Dependencies:** Sprint 2
**Estimated Time:** 2 hours

### Sprint 6: Color Scheme (Tasks 16)
**Priority:** MEDIUM - Brand consistency
**Dependencies:** Sprint 1
**Estimated Time:** 30 minutes

### Sprint 7: Optimization (Tasks 17)
**Priority:** LOW - Performance enhancement
**Dependencies:** Sprint 6
**Estimated Time:** 1 hour

### Sprint 8: Testing & Documentation (Tasks 18-20)
**Priority:** LOW - Quality assurance
**Dependencies:** All sprints
**Estimated Time:** 2 hours

**Total Estimated Time:** 13.5 hours

---

## 📊 Success Criteria

### Functional Requirements
- [ ] CSV loads successfully with all 78 pages
- [ ] Table displays all 78 pages correctly
- [ ] Filters work (Page Type, Mobile Responsive, Issues)
- [ ] Search functionality works
- [ ] Clicking row shows details panel
- [ ] Details panel displays correct screenshot
- [ ] Details panel shows all detected issues
- [ ] Issues column shows count badge
- [ ] Close button hides details panel
- [ ] All 78 screenshots are accessible
- [ ] Responsive layout works on desktop, tablet, mobile
- [ ] No JavaScript errors in console

### Performance Requirements
- [ ] Page loads in < 2 seconds
- [ ] Filters apply instantly (<100ms)
- [ ] Row selection is instant
- [ ] Details panel appears instantly (<100ms)
- [ ] Screenshot loads on demand (not preloaded)
- [ ] Scrolling is smooth at 60fps

### Accessibility Requirements
- [ ] All interactive elements have ARIA labels
- [ ] Keyboard navigation works (tab to filters, tab to rows)
- [ ] Focus indicators are visible
- [ ] Color contrast is sufficient (WCAG AA)
- [ ] Screen reader compatible

### Code Quality Requirements
- [ ] Code is well-commented
- [ ] Functions have single responsibility
- [ ] No code duplication
- [ ] Error handling is comprehensive
- [ ] Follows DRY principle

---

## 📁 Developer Notes

### CSV Column Mapping
```javascript
const COLUMN_MAP = {
    PAGE_URL: 0,           // Page URL
    PAGE_TITLE: 1,         // Page Title
    PAGE_TYPE: 2,          // Page Type
    TEMPLATE_USED: 3,       // Template Used
    INBOUND_LINKS: 4,       // Inbound Links
    OUTBOUND_LINKS: 5,      // Outbound Links
    HUMAN_ISSUES: 6,         // Human Identified Issues
    SEVERITY: 7,            // Issue Severity
    ISSUE_TYPE: 8,             // Issue Type
    DETECTED_BY: 9,         // Detected By
    FIX_STATUS: 10,          // Fix Status
    PR_LINK: 11,              // PR Link
    LAST_REVIEWED: 12,       // Last Reviewed Date
    VIDEO_WORKING: 13,        // Video Embed Working
    AUDIO_WORKING: 14,        // Audio Embed Working
    IMAGE_LOADED: 15,         // Image Assets Loaded
    MOBILE_RESPONSIVE: 16,    // Mobile Responsive
    SCREENSHOT_PATH: 17         // Screenshot Path
};
```

### Filename Conversion Algorithm
```javascript
function convertPageToFilename(pageUrl) {
    let filename = pageUrl.replace('.html', '');
    filename = filename.replace('/', '_');
    while (filename.includes('__')) {
        filename = filename.replace('__', '_');
    }
    return filename + '.png';
}
```

### Issues Parsing Algorithm
```javascript
function parseIssues(issuesString) {
    if (!issuesString) return [];
    return issuesString.split('; ').map(s => s.trim()).filter(s => s);
}
```

---

## 🚀 Resources

### Learning Resources
- PapaParse Documentation: https://www.papaparse.com/docs
- ARIA Guidelines: https://www.w3.org/WAI/ARIA/apg/
- WCAG Color Contrast: https://www.w3.org/WAI/WCAG21/quickref/#contrast-minimum
- CSS Grid Layout: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout
- Responsive Design: https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS/Media_Queries/Using_Media_Queries

### Similar Projects
- CSV Viewer libraries: Papaparse, D3.js, Tableau
- Dashboard examples: AdminLTE, CoreUI, Metronic

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
**Author:** AI Assistant
**Status:** Ready for Implementation
