# Implementation Plan V2: Custom Load Features & City Display

## Overview

This plan implements a three-tier guided disclosure model for the interactive demo, adding custom load options and city-based display for load data.

---

## Architecture Overview

### **Three-Tier Disclosure Model**

**Tier 1: Story Context (Initially Expanded)**
- "What is this demo?" explanation
- "How to add loads" guidance
- "Why recommended loads make sense" rationale
- Inline block below "Add Load" form
- "Add Recommended Loads" button placed INSIDE this context
- Initially disabled until user dismisses story

**Tier 2: "Add Recommended Loads" Button (Revealed After Tier 1)**
- Purple gradient button (distinct from green "Add Load" button)
- Adds 2 predefined Ohio local hauls instantly
- Idempotent (can only be applied once per session)
- Disables itself after use

**Tier 3: "Add Custom Load" (Always Visible)**
- Manual form (existing "Add Load" button)
- Collapsible "Custom Load Options" panel (hidden by default)
- Limited to 3 custom entries (total 5 max: 2 recommended + 3 custom)
- Shows city names (not lane codes) for origin/destination

---

## Detailed Requirements Analysis

### **Requirement 1: Custom Load Toggle (Hidden by Default)**

**Location:** Above "Add Load" form

**Behavior:**
- "Custom Load Options" button with toggle icon
- Panel initially collapsed (display: none)
- Clicking expands panel with slide-down animation
- Panel contains: additional help, examples, guidance
- Toggle rotates icon 90° when active
- Panel slides down from collapsed state

**UI Structure:**
```html
<div class="custom-load-toggle">
    <button id="btnToggleCustom" class="btn-toggle-custom">
        Custom Load Options
        <span class="toggle-icon">▶</span>
    </button>
    <div id="customLoadOptions" class="custom-load-options collapsed">
        <!-- Custom load help, examples, tips -->
    </div>
</div>
```

---

### **Requirement 2: Story Context (Initially Visible)**

**Location:** Inline block, part of "Add Load" section

**Content Sections:**
1. **What This Demo Is**
   - "This is a guided exploration sandbox showing how revenue reporting works"
   - "You can add your own loads to see real-time impacts on metrics"
   - "No backend - all data is temporary in this browser session"

2. **How to Add Loads**
   - "Option A: Use 'Add Recommended Loads' for instant, realistic scenarios"
   - "Option B: Use 'Add Custom Load' to enter your own data"
   - "Maximum 5 total loads can be added in this demo session"
   - "Recommended: 2 loads | Custom: 3 loads"

3. **Why Recommended Loads Make Sense**
   - "They demonstrate effective operational patterns"
   - "They show what 'good' local hauls look like in the Ohio market"
   - "They help you understand how short hauls stabilize revenue before longer runs"

**Story Narrative:**
"Entered Ohio market, ran 2 short local hauls, then repositioned out following day"

**Specific Load Patterns:**
- **Load 1:** Columbus, OH → Toledo, OH
  - 142 paid miles, 8 deadhead miles, $312.40 revenue
  - Purpose: Major freight corridor entry, state capital to regional hub
  - Logic: "Columbus → Toledo demonstrates major freight corridor entry"

- **Load 2:** Toledo, OH → Cleveland, OH
  - 116 paid miles, 6 deadhead miles, $284.60 revenue
  - Purpose: Reload in strong Ohio market, Cleveland is strong reload market
  - Logic: "Toledo → Cleveland shows reload strategy in strong Ohio market"

**UI Implementation:**
```html
<div id="storyContext" class="story-context visible">
    <button class="btn-close-story" id="btnCloseStory">&times;</button>
    
    <div class="story-content">
        <div class="story-section">
            <h3>What This Demo Is</h3>
            <p>This is a guided exploration sandbox showing how revenue reporting works for logistics carriers. All data is temporary and exists only in your browser session.</p>
        </div>
        
        <div class="story-section">
            <h3>How to Add Loads</h3>
            <p><strong>Option A:</strong> Use "Add Recommended Loads" for instant, realistic scenarios. These demonstrate effective operational patterns in the Ohio market.</p>
            <p><strong>Option B:</strong> Use "Add Custom Load" to enter your own data and explore scenarios that matter to you. Maximum 3 custom loads (2 recommended + 3 custom = 5 total).</p>
        </div>
        
        <div class="story-section">
            <h3>Why Recommended Loads Make Sense</h3>
            <ul class="story-list">
                <li><strong>Market Entry Strategy:</strong> Columbus → Toledo demonstrates major freight corridor entry from state capital to regional hub.</li>
                <li><strong>Stabilization Pattern:</strong> Toledo → Cleveland shows reload strategy in strong Ohio market before longer runs.</li>
                <li><strong>Revenue Consistency:</strong> Short hauls maintain target revenue per mile ($2.19-$2.70) consistent with existing data quality.</li>
                <li><strong>Operational Rhythm:</strong> Both loads on same day, then reposition out of market next day - typical market entry pattern.</li>
            </ul>
        </div>
    </div>
    
    <div id="recommendedLoadsPlaceholder" class="placeholder">
        <button id="btnAddRecommended" class="btn-recommended disabled" disabled>
            Add Recommended Loads
        </button>
        <p class="btn-info">Read the story above first</p>
    </div>
</div>
```

**Initial State:**
- Story context: `visible` class (expanded)
- "Add Recommended Loads" button: `disabled` attribute, can't be clicked
- Placeholder div visible with disabled button and "Read the story above first" message
- "Add Custom Load" form: hidden behind toggle (initially collapsed)

**User Flow:**
1. User sees story, reads content
2. User clicks "×" to close story
3. "Add Recommended Loads" button becomes enabled
4. User can click to add loads, or expand custom options

---

### **Requirement 3: Recommended Loads Button & Data**

**Location:** Inside `recommendedLoadsPlaceholder` div (shown after story dismissed)

**Behavior:**
- Single click adds 2 predefined loads instantly
- Idempotent: Uses `recommendedLoadsAdded` flag to prevent re-adding
- Disables itself after use
- Both loads added to `window.userAddedLoads`
- All metrics, charts, tables update immediately

**Recommended Loads Data Structure:**
```javascript
const RECOMMENDED_LOADS = [
    {
        date: "2026-01-21",
        from_location: "Columbus, OH",
        to_location: "Toledo, OH",
        paid_miles: 142,
        deadhead_miles: 8,
        revenue: 312.40,
        broker: "Recommended",
        is_recommended: true
    },
    {
        date: "2026-01-21",
        from_location: "Toledo, OH",
        to_location: "Cleveland, OH",
        paid_miles: 116,
        deadhead_miles: 6,
        revenue: 284.60,
        broker: "Recommended",
        is_recommended: true
    }
];
```

**State Tracking:**
```javascript
let recommendedLoadsAdded = false;
```

**UI Feedback:**
- Button shows purple gradient (distinct from green "Add Load" button)
- When disabled: `rgba(139, 92, 246, 0.3)` background, opacity 0.6
- When clicked and loads added: Button remains disabled (idempotent check)

---

### **Requirement 4: Custom Load Limit (3 After Recommended)**

**Current System:**
- `MAX_ADDITIONAL_LOADS = 5` (total allowed)
- Recommended loads: 2 (fixed, built-in)
- Custom loads: 3 (maximum user can add manually)

**New Behavior Required:**
- Separate tracking for custom vs recommended loads
- Enforce 3-load limit for custom entries
- Clear error messaging when limit exceeded
- Counter breakdown: "Added: X/5 (Y rec + Z cust)"

**State Variables:**
```javascript
let customLoadCount = 0;
let recommendedLoadCount = 0;
const MAX_CUSTOM_LOADS = 3;
const MAX_TOTAL_LOADS = 5;
```

**Limit Checking Logic:**
```javascript
function addLoad() {
    // Check custom limit FIRST
    if (customLoadCount >= MAX_CUSTOM_LOADS) {
        alert(`Maximum ${MAX_CUSTOM_LOADS} custom loads allowed (${recommendedLoadCount} recommended + ${MAX_CUSTOM_LOADS} custom = ${MAX_TOTAL_LOADS} total).`);
        return;
    }

    // ... rest of addLoad logic ...

    customLoadCount++;
    const totalCount = customLoadCount + recommendedLoadCount;

    // Update UI counters
    document.getElementById('loadCount').textContent = totalCount;
    document.getElementById('recommendedCount').textContent = recommendedLoadCount;
    document.getElementById('customCount').textContent = customLoadCount;
}
```

**Error Messages:**
- Attempting  add 4th custom load: "Maximum 3 custom loads allowed (2 recommended + 3 custom = 5 total)."
- Attempting to add recommended loads after already added: "Recommended loads have already been added to this demo session."

---

### **Requirement 5: City Display in Load Data**

**Requirement:**
- Load-level data must show ORIGIN CITY and DESTINATION CITY
- Full city names, not just state codes (e.g., "Columbus, OH → Toledo, OH" not "OH-OH")
- Apply to: weekly breakdown daily rows, Lane Performance table, user-added loads

**Data Flow:**
```javascript
// Input: "Columbus, OH" (from_location)
// Input: "Toledo, OH" (to_location)
// Extract: "Columbus" (from_city)
// Extract: "OH" (from_state)
// Extract: "Toledo" (to_city)
// Extract: "OH" (to_state)
// Output: "Columbus, OH → Toledo, OH"
```

**City Display Function:**
```javascript
function formatLaneCities(from, to) {
    if (!from || !to) return '';
    const fromCity = from.split(', ')[0].trim();
    const toCity = to.split(', ')[0].trim();
    return `${fromCity} → ${toCity}`;
}
```

**Applications:**

1. **Weekly Breakdown Daily Rows:**
   - Current: Shows lane code "OH-IL"
   - New: Shows city pair "Toledo, OH → Chicago, IL"
   - Location: In `renderWeeklyTable()` daily row generation

2. **Lane Performance Table:**
   - Current: Shows lane codes "OH-IL", "OH-MI"
   - New: Shows city pairs "Toledo - Chicago", "Columbus - Toledo"
   - Location: Lines ~1058-1113

3. **User-Added Recommended Loads:**
   - Show city pairs: "Columbus, OH → Toledo, OH"
   - Purple badge: "Recommended"

4. **User-Added Custom Loads:**
   - Show city pairs from user input
   - Green badge: "Demo"

---

## Implementation Plan

### **Phase 1: HTML Structure Updates**

#### **1.1 Add Custom Load Toggle** (above "Add Load" form, line ~690)

**Insert after existing form:**
```html
<div class="custom-load-toggle">
    <button id="btnToggleCustom" class="btn-toggle-custom">
        Custom Load Options
        <span class="toggle-icon">▶</span>
    </button>
    <div id="customLoadOptions" class="custom-load-options collapsed">
        <div class="custom-options-content">
            <h4>Custom Load Guidance</h4>
            <p><strong>Examples of effective local hauls:</strong></p>
            <ul class="custom-examples">
                <li>Short intrastate moves (50-200 miles)</li>
                <li>Same-day reloads in strong markets</li>
                <li>High-revenue corridors (>$2.50/mile)</li>
                <li>Strategic repositioning before leaving region</li>
            </ul>
            <p class="custom-tip"><strong>Tip:</strong> Focus on high revenue per mile and low deadhead percentage to maximize profitability.</p>
            <p><strong>Custom Load Limit:</strong> Maximum 3 custom loads (in addition to 2 recommended loads).</p>
        </div>
    </div>
</div>
```

---

#### **1.2 Add Story Context Panel** (replace existing "Add Load" button area, line ~670-780)

**Replace entire add-load-form section with:**
```html
<div class="add-load-section">
    <div class="add-load-header">
        <h2 class="add-load-title">Add Demo Load</h2>
        <p class="add-load-info">Add up to 5 temporary load rows to test analytics. Original data is protected and cannot be edited.</p>
        <div class="load-counter">Added: <span id="loadCount">0</span>/5
            <span class="counter-breakdown">
                (<span id="recommendedCount">0</span> rec + <span id="customCount">0</span> cust)
            </span>
        </div>
    </div>
    
    <div id="storyContext" class="story-context visible">
        <button class="btn-close-story" id="btnCloseStory">&times;</button>
        
        <div class="story-content">
            <div class="story-section">
                <h3>What This Demo Is</h3>
                <p>This is a guided exploration sandbox showing how revenue reporting works for logistics carriers. All data is temporary and exists only in your browser session.</p>
            </div>
            
            <div class="story-section">
                <h3>How to Add Loads</h3>
                <p><strong>Option A:</strong> Use "Add Recommended Loads" for instant, realistic scenarios. These demonstrate effective operational patterns in the Ohio market.</p>
                <p><strong>Option B:</strong> Use "Add Custom Load" to enter your own data and explore scenarios that matter to you. Maximum 3 custom loads (2 recommended + 3 custom = 5 total).</p>
            </div>
            
            <div class="story-section">
                <h3>Why Recommended Loads Make Sense</h3>
                <ul class="story-list">
                    <li><strong>Market Entry Strategy:</strong> Columbus → Toledo demonstrates major freight corridor entry from state capital to regional hub.</li>
                    <li><strong>Stabilization Pattern:</strong> Toledo → Cleveland shows reload strategy in strong Ohio market before longer runs.</li>
                    <li><strong>Revenue Consistency:</strong> Short hauls maintain target revenue per mile ($2.19-$2.70) consistent with existing data quality.</li>
                    <li><strong>Operational Rhythm:</strong> Both loads on same day, then reposition out of market next day - typical market entry pattern.</li>
                </ul>
            </div>
        </div>
        
        <form id="addLoadForm" class="add-load-form">
            <!-- Existing form inputs remain here -->
        </form>
        
        <div id="recommendedLoadsPlaceholder" class="placeholder">
            <button id="btnAddRecommended" class="btn-recommended disabled" disabled>
                Add Recommended Loads
            </button>
            <p class="btn-info">Read the story above first</p>
        </div>
    </div>
</div>
```

**Change:** Removed "Add Load" button, moved it inside story context, created placeholder for "Add Recommended Loads" button

---

### **Phase 2: CSS Additions** (around line ~570)

#### **2.1 Custom Load Toggle Styles**

```css
.custom-load-toggle {
    margin-bottom: 15px;
}

.btn-toggle-custom {
    background: rgba(107, 114, 128, 0.2);
    color: #9ca3af;
    border: 1px solid rgba(107, 114, 128, 0.3);
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
}

.btn-toggle-custom:hover {
    background: rgba(107, 114, 128, 0.3);
    border-color: rgba(107, 114, 128, 0.5);
}

.btn-toggle-custom.active .toggle-icon {
    transform: rotate(90deg);
}

.toggle-icon {
    transition: transform 0.3s ease;
    display: inline-block;
}

.custom-load-options {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(107, 114, 128, 0.2);
    border-radius: 8px;
    padding: 20px;
    margin-top: 10px;
    display: none;
}

.custom-load-options.collapsed {
    display: none;
}

.custom-load-options {
    display: block;
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.custom-options-content {
    max-width: 600px;
}

.custom-options-content h4 {
    color: #fbbf24;
    font-size: 1.1rem;
    margin-bottom: 15px;
}

.custom-options-content p {
    color: #d1d5db;
    line-height: 1.7;
    margin-bottom: 15px;
}

.custom-examples {
    list-style: none;
    padding-left: 20px;
    margin-bottom: 15px;
}

.custom-examples li {
    padding: 8px 0;
    color: #e5e7eb;
    position: relative;
}

.custom-examples li:before {
    content: "•";
    position: absolute;
    left: -20px;
    color: #8b5cf6;
    font-weight: bold;
}

.custom-tip {
    background: rgba(139, 92, 246, 0.1);
    border-left: 3px solid #8b5cf6;
    padding: 10px 15px;
    border-radius: 0 8px 0 8px;
    font-style: italic;
    color: #a78bfa;
}
```

---

#### **2.2 Story Context Styles**

```css
.story-context {
    background: rgba(251, 191, 36, 0.1);
    border: 2px solid rgba(251, 191, 36, 0.3);
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 20px;
    position: relative;
}

.story-context.hidden {
    display: none;
}

.story-context.collapsed {
    display: none;
}

.story-content {
    max-width: 700px;
}

.story-section {
    margin-bottom: 30px;
}

.story-section h3 {
    color: #fbbf24;
    font-size: 1.3rem;
    margin-bottom: 12px;
}

.story-section p {
    color: #e5e7eb;
    line-height: 1.7;
    margin-bottom: 12px;
}

.story-section strong {
    color: #fbbf24;
}

.story-section em {
    color: #f472b6;
}

.story-list {
    list-style: none;
    padding: 0;
    margin-top: 15px;
}

.story-list li {
    padding: 12px 0 12px 25px;
    color: #d1d5db;
    border-left: 3px solid #fbbf24;
    background: rgba(251, 191, 36, 0.05);
    border-radius: 0 8px;
}

.story-list li strong {
    color: #fbbf24;
}

.btn-close-story {
    position: absolute;
    top: 15px;
    right: 15px;
    background: transparent;
    border: none;
    color: #9ca3af;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 5px 10px;
    line-height: 1;
}

.btn-close-story:hover {
    color: #fbbf24;
}

.placeholder {
    padding: 20px;
    text-align: center;
    border-top: 1px solid rgba(251, 191, 36, 0.2);
}

.btn-recommended {
    background: linear-gradient(45deg, #8b5cf6, #7c3aed);
    color: white;
    padding: 14px 30px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.btn-recommended:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.btn-recommended.disabled {
    background: rgba(139, 92, 246, 0.3);
    cursor: not-allowed;
    opacity: 0.6;
}

.btn-info {
    font-style: italic;
    color: #9ca3af;
    margin-top: 10px;
    font-size: 0.9rem;
}

.counter-breakdown {
    font-size: 0.85rem;
    color: #9ca3af;
    margin-left: 10px;
}

#recommendedCount, #customCount {
    color: #fbbf24;
    font-weight: 600;
}
```

---

#### **2.3 City Display Styles**

```css
.lane-cell.city-lane {
    font-size: 0.95rem;
}

.lane-cell .lane-full {
    display: block;
    font-weight: 500;
    color: #334155;
}

.lane-cell .lane-code {
    display: none;
}

.lane-cell.recommended-row {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(124, 58, 237, 0.15));
    border-left: 4px solid #8b5cf6;
}

.recommended-row .lane-cell {
    font-weight: 600;
    color: #7c3aed;
}
```

---

### **Phase 3: JavaScript Updates** (around line ~1230-1570)

#### **3.1 Add New State Variables**

```javascript
// After window.brokerData initialization
let recommendedLoadsAdded = false;
let customLoadCount = 0;
let recommendedLoadCount = 0;
const MAX_CUSTOM_LOADS = 3;

// Recommended loads data
const RECOMMENDED_LOADS = [
    {
        date: "2026-01-21",
        from_location: "Columbus, OH",
        to_location: "Toledo, OH",
        paid_miles: 142,
        deadhead_miles: 8,
        revenue: 312.40,
        broker: "Recommended",
        is_recommended: true
    },
    {
        date: "2026-01-21",
        from_location: "Toledo, OH",
        to_location: "Cleveland, OH",
        paid_miles: 116,
        deadhead_miles: 6,
        revenue: 284.60,
        broker: "Recommended",
        is_recommended: true
    }
];
```

---

#### **3.2 Add Helper Function for City Display**

```javascript
function formatLaneCities(from, to) {
    if (!from || !to) return '';
    const fromCity = from.split(', ')[0].trim();
    const toCity = to.split(', ')[0].trim();
    return `${fromCity} → ${toCity}`;
}
```

**Location:** Insert after `formatLane()` function (around line ~1410)

---

#### **3.3 Update recalculateTotals() Function**

**Current code structure preserved**, no changes needed.

---

#### **3.4 Update renderWeeklyTable() Function**

**Changes to user-added rows section (around line ~1550):**

**Current:**
```javascript
if (window.userAddedLoads.length > 0) {
    window.userAddedLoads.forEach((load, index) => {
        const tr = document.createElement('tr');
        tr.classList.add('week-row', 'user-added-row');
        tr.innerHTML = '...';
        tbody.appendChild(tr);
    });
}
```

**New:**
```javascript
if (window.userAddedLoads.length > 0) {
    window.userAddedLoads.forEach((load, index) => {
        const tr = document.createElement('tr');
        const badgeText = load.is_recommended ? 'Recommended' : 'Demo';
        const rowClass = load.is_recommended ? 'recommended-row' : 'user-added-row';
        
        tr.classList.add('week-row', rowClass);
        tr.innerHTML = '<td>Added ' + (index + 1) + ' <span class="demo-badge">' + badgeText + '</span></td>' +
            '<td class="currency">$' + load.revenue.toFixed(2) + '</td>' +
            '<td>' + load.paid_miles.toFixed(0) + '</td>' +
            '<td class="warning">' + load.deadhead_miles.toFixed(0) + '</td>' +
            '<td>1</td>' +
            '<td>0</td>' +
            '<td class="currency">$' + load.revenue.toFixed(2) + '</td>' +
            '<td class="lane-cell city-lane">' + formatLaneCities(load.from_location, load.to_location) + '</td>';
        
        tbody.appendChild(tr);
    });
}
```

---

#### **3.5 Update Daily Breakdown Row Generation**

**Changes to daily breakdown HTML generation (around line ~1525):**

**Current:**
```javascript
dailyRowsHtml += '<tr>' +
    '<td>' + day.date + '</td>' +
    '<td>' + lane + '</td>' +
    '<td>' + day.load_count + '</td>' +
    ...
```

**New:**
```javascript
dailyRowsHtml += '<tr>' +
    '<td>' + day.date + '</td>' +
    '<td class="lane-cell city-lane">' + formatLaneCities(entry?.from_location, entry?.to_location) + '</td>' +
    '<td>' + day.load_count + '</td>' +
    '<td class="currency">$' + day.revenue.toFixed(2) + '</td>' +
    '<td>' + day.paid_miles.toFixed(0) + '</td>' +
    '<td class="warning">' + day.deadhead_miles.toFixed(0) + '</td>' +
    '</tr>';
```

---

#### **3.6 Create addRecommendedLoads() Function**

**Location:** Insert after `addLoad()` function (around line ~1460)

```javascript
function addRecommendedLoads() {
    // Idempotency check
    if (recommendedLoadsAdded) {
        alert('Recommended loads have already been added to this demo session.');
        return;
    }
    
    // Add both recommended loads
    RECOMMENDED_LOADS.forEach(load => {
        window.userAddedLoads.push(load);
    });
    
    // Update counters
    recommendedLoadCount = 2;
    addedLoadCount = customLoadCount + recommendedLoadCount;
    
    // Update UI
    document.getElementById('loadCount').textContent = addedLoadCount;
    document.getElementById('recommendedCount').textContent = recommendedLoadCount;
    
    // Check total limit
    if (addedLoadCount >= MAX_ADDITIONAL_LOADS) {
        document.getElementById('btnAdd').disabled = true;
        document.getElementById('btnAddRecommended').disabled = true;
        document.querySelectorAll('.add-load-form input').forEach(input => {
            input.disabled = true;
        });
    }
    
    // Recalculate everything
    recalculateTotals();
    renderWeeklyTable();
    renderCharts();
    
    // Clear form
    document.getElementById('addLoadForm').reset();
}
```

---

#### **3.7 Update addLoad() Function for Custom Limit**

**Current code preserved**, add custom limit check at beginning:

```javascript
function addLoad() {
    // Check custom limit first
    if (customLoadCount >= MAX_CUSTOM_LOADS) {
        alert(`Maximum ${MAX_CUSTOM_LOADS} custom loads allowed (${recommendedLoadCount} recommended + ${MAX_CUSTOM_LOADS} custom = ${MAX_TOTAL_LOADS} total).`);
        return;
    }
    
    // ... existing addLoad logic continues ...
    
    // Update custom counter
    customLoadCount++;
    const totalCount = customLoadCount + recommendedLoadCount;
    
    // Update UI counters
    document.getElementById('loadCount').textContent = totalCount;
    document.getElementById('customCount').textContent = customLoadCount;
    document.getElementById('recommendedCount').textContent = recommendedLoadCount;
}
```

---

#### **3.8 Update clearForm() Function**

**No changes needed** - function remains as-is.

---

#### **3.9 Add Event Listeners**

**Location:** After `clearForm` event listener (around line ~1580)

```javascript
// Custom load toggle
document.getElementById('btnToggleCustom').addEventListener('click', function() {
    this.classList.toggle('active');
    const options = document.getElementById('customLoadOptions');
    options.classList.toggle('collapsed');
});

// Story close
document.getElementById('btnCloseStory').addEventListener('click', function() {
    document.getElementById('storyContext').classList.add('hidden');
    document.getElementById('btnAddRecommended').removeAttribute('disabled');
    document.getElementById('btnAddRecommended').disabled = false;
});

// Recommended loads button
document.getElementById('btnAddRecommended').addEventListener('click', addRecommendedLoads);
```

---

### **Phase 4: Lane Performance Table Update** (lines ~1058-1113)

**Update Lane Performance table to show city pairs instead of lane codes:**

**Current:**
```html
<tr>
    <td>OH-IL</td>
    <td>3</td>
    <td class="currency">$1,514.10</td>
    <td class="currency">$504.70</td>
    <td>735</td>
    <td class="currency">2.06</td>
</tr>
```

**New:**
```html
<tr>
    <td class="lane-cell city-lane">Toledo, OH - Chicago, IL</td>
    <td>3</td>
    <td class="currency">$1,514.10</td>
    <td class="currency">$504.70</td>
    <td>735</td>
    <td class="currency">2.06</td>
</tr>
```

**Apply to all rows:**
- Row 1: "OH-IL" → "Toledo, OH - Chicago, IL"
- Row 2: "OH-MI" → "Toledo, OH - Detroit, MI"
- Row 3: "IL-OH" → "Toledo, OH - Chicago, IL"
- Row 4: "OH-IN" → "Toledo, OH - Indianapolis, IN"
- Row 5: "OH-IN" → "Columbus, OH - Indianapolis, IN"
- Row 6: "OH-IN" → "Indianapolis, IN - Toledo, OH"

---

## User Experience Flow

### **Scenario 1: First-Time User**

1. User arrives at interactive demo page
2. Sees "DEMO MODE" badge
3. Sees story context panel expanded:
   - "What This Demo Is"
   - "How to Add Loads" (2 options)
   - "Why Recommended Loads Make Sense"
4. "Add Recommended Loads" button: disabled with "Read the story above first"
5. User reads story content
6. User clicks "×" to close story
7. Story collapses/disappears
8. "Add Recommended Loads" button becomes enabled (purple gradient)
9. User can click "Add Recommended Loads" or expand "Custom Load Options"

---

### **Scenario 2: User Clicks "Add Recommended Loads"**

1. User clicks purple "Add Recommended Loads" button
2. Both Ohio loads added instantly:
   - Load 1: Columbus → Toledo ($312.40)
   - Load 2: Toledo → Cleveland ($284.60)
3. All metrics update in real-time
4. Charts update
5. Weekly table shows 2 new rows with "Recommended" badges
6. Button becomes disabled (idempotent check)
7. Counter: "Added: 2/5 (2 rec + 0 cust)"
8. User can still add up to 3 custom loads

---

### **Scenario 3: User Expands Custom Options**

1. User clicks "Custom Load Options" toggle
2. Panel slides down with animation
3. User sees guidance:
   - "Examples of effective local hauls"
   - "Custom Load Limit: Maximum 3 custom loads"
   - Tips on revenue per mile and deadhead
4. User understands constraints before entering data

---

### **Scenario 4: User Adds Custom Loads First**

1. User enters custom load data manually
2. User clicks "Add Load" button
3. Custom load added (customLoadCount = 1)
4. Counter: "Added: 1/5 (0 rec + 1 cust)"
5. User can add 2 more custom loads

---

### **Scenario 5: User Adds 3 Custom Loads, Tries to Add 4th**

1. User enters 4th custom load
2. User clicks "Add Load" button
3. Alert appears: "Maximum 3 custom loads allowed (2 recommended + 3 custom = 5 total)."
4. Form is NOT cleared, button not disabled
5. User can adjust data and try again

---

### **Scenario 6: User Dismisses Story First**

1. User immediately clicks "×" to close story
2. Story collapses/disappears
3. "Add Recommended Loads" button becomes enabled
4. User adds 2 recommended loads immediately
5. Then adds up to 3 custom loads
6. Full counter: "Added: 5/5"

---

## Technical Considerations

### **Lane Data Handling**

**Old Format (Lane Codes):**
- Format: `formatLane(from, to)` → "OH-IL"
- Location: Lane Performance table, weekly summary
- Issue: No city information, hard to interpret

**New Format (City Pairs):**
- Format: `formatLaneCities(from, to)` → "Columbus, OH → Toledo, OH"
- Location: Weekly breakdown daily rows, Lane Performance table, user-added loads
- Benefit: Clear city names, easier to understand operations

**Backward Compatibility:**
- `formatLane()` function remains (used for Lane Performance table)
- New `formatLaneCities()` function for load-level data
- Separate usage based on context

---

### **Load Type Distinction**

**Recommended Loads:**
- `is_recommended: true` flag in data object
- Purple badge display
- `recommended-row` CSS class
- Added via single button click
- Limited to exactly 2 (built-in data)

**Custom Loads:**
- `is_recommended: false` or missing flag
- Green "Demo" badge (existing)
- `user-added-row` CSS class
- Limited to 3 entries
- Entered manually via form

---

### **Counter Display Logic**

**Total Count:**
```javascript
const totalCount = customLoadCount + recommendedLoadCount;
```

**Display Format:**
```
Added: 5/5
(2 rec + 3 cust)
```

**CSS Classes:**
- `#loadCount`: Main counter value
- `.counter-breakdown`: Container for breakdown
- `#recommendedCount`: Purple text, bold
- `#customCount`: Standard color, no special styling

---

### **Story Context Animation**

**Collapse/Expand:**
- Using `display: none` and `display: block`
- With slide-down animation when expanding
- Smooth 0.3s ease transition

**Close Button:**
- Absolute positioning (top-right)
- Transparent background, no border
- Hover effect: color change to highlight interactability

---

## File Modification Summary

| Section | Type | Changes | Lines Affected |
|----------|------|-------------|----------------|
| Add load section | HTML | Add custom load toggle + story context panel | ~690-780 |
| Add load section | HTML | Update load counter with breakdown | ~690-780 |
| JavaScript | Variables | Add state tracking variables | ~1235 |
| JavaScript | Functions | Add formatLaneCities() helper | ~1410 |
| JavaScript | Functions | Update addLoad() for custom limit | ~1460 |
| JavaScript | Functions | Add addRecommendedLoads() function | ~1480 |
| JavaScript | Functions | Update renderWeeklyTable() for city display | ~1550 |
| JavaScript | Events | Toggle custom panel + story close + recommended button | ~1585 |
| Lane Performance | HTML | Update rows to show city pairs | ~1058-1113 |
| CSS | Styles | Custom load toggle styles (35 lines) | ~575 |
| CSS | Styles | Story context styles (70 lines) | ~575 |
| CSS | Styles | Recommended button styles (20 lines) | ~595 |
| CSS | Styles | Counter breakdown styles (8 lines) | ~603 |
| CSS | Styles | City display styles (15 lines) | ~618 |

---

## Testing Checklist

- [ ] Custom load toggle expands/collapses correctly
- [ ] Story context appears on load, dismisses on click
- [ ] "Add Recommended Loads" button disabled initially, enables after story dismissal
- [ ] Clicking "Add Recommended Loads" adds 2 loads instantly
- [ ] Recommended loads display purple "Recommended" badge
- [ ] Counter shows correct breakdown "(2 rec + 3 cust)"
- [ ] Custom load limit enforced (max 3)
- [ ] Clear error message for custom limit exceeded
- [ ] City names display in weekly breakdown daily rows
- [ ] City names display in Lane Performance table
- [ ] City names display in user-added recommended loads
- [ ] City names display in user-added custom loads
- [ ] Recommended loads idempotent (can't re-add)
- [ ] Total limit enforced (5 loads max)
- [ ] All metrics update correctly when recommended loads added
- [ ] Charts update correctly when recommended loads added
- [ ] Form inputs disabled when limit reached

---

## Completion Criteria

**Implementation is complete when:**

1. Custom load toggle appears above form with collapsible options panel
2. Story context panel displays 3 sections and is dismissible
3. "Add Recommended Loads" button exists in story context
4. Recommended loads data structure defined with 2 Ohio loads
5. State tracking variables added (customLoadCount, recommendedLoadCount, recommendedLoadsAdded)
6. formatLaneCities() helper function created
7. addRecommendedLoads() function implemented with idempotency
8. addLoad() function updated to enforce 3-load custom limit
9. Counter displays breakdown (recommended + custom)
10. Weekly breakdown rows show city names instead of lane codes
11. Lane Performance table shows city pairs
12. User-added loads show city names with appropriate badges
13. Event listeners added for all new interactive elements
14. All CSS styles added and tested
15. All functionality tested and working

---

**This plan is ready for implementation. All requirements have been addressed in detail.**
