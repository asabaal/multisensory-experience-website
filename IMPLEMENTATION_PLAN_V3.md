# Implementation Plan V3: Reflective Orientation & Progressive Disclosure

## Overview

This plan implements a **four-tier progressive disclosure model** for the interactive demo, adding reflective orientation narrative that appears after recommended loads, proper disclosure for custom load functionality, and fixes critical JavaScript errors preventing charts from rendering.

---

## Architecture Overview

### **Four-Tier Disclosure Model**

**Tier 1: Story Context (Initially Expanded)**
- "What is this demo?" explanation
- "How to add loads" guidance
- "Why recommended loads make sense" rationale
- Close button to dismiss context
- "Add Recommended Loads" button inside context (disabled initially)

**Tier 2: "Add Recommended Loads" Button (Enabled After Tier 1)**
- Purple gradient button (distinct from green "Add Load" button)
- Adds 2 predefined Ohio local hauls instantly
- Idempotent (can only be applied once per session)
- Disables itself after use

**Tier 3: Reflective Orientation Narrative (Revealed After Tier 2)**
- 5 language blocks that appear after recommended loads are added
- Helps user translate demo action → real life strategy
- Teaches what "business intelligence" actually means
- Soft sells the product as an ongoing strategic mirror
- Never says "you should" - asks them to notice

**Tier 4: "Add Custom Load" Section (Revealed After Tier 3)**
- Only appears after recommended loads are added AND narrative shown
- "Add Custom Load" button toggles form visibility
- Form is hidden by default (collapsed state)
- Limited to 3 custom entries (total 5 max: 2 recommended + 3 custom)
- Shows city names (not lane codes) for origin/destination

---

## Critical Issues to Fix

### **Issue 1: Custom Load Toggle Button (REMOVE)**
- **Current:** Custom load toggle button at top of page (lines 960-979)
- **Problem:** Should not exist - custom load functionality should be hidden until after recommended loads
- **Action:** Delete entire `.custom-load-toggle` section and all related CSS/JS

### **Issue 2: Custom Load Form Visibility (RESTRUCTURE)**
- **Current:** Custom load form is always visible inside story context
- **Problem:** Should be hidden initially, only appear after recommended loads
- **Action:** Move form to separate section that's hidden by default

### **Issue 3: Button Ordering (FIX)**
- **Current:** Custom load form appears before recommended button
- **Required:** "Add Recommended Loads" button first, then "Add Custom Load" section

### **Issue 4: JavaScript Syntax Error (FIX)**
- **Error:** `const MAX_ADDITIONAL_LOADS = 5;` declared twice (lines 1577 and 1613)
- **Action:** Remove duplicate declaration at line 1613

### **Issue 5: Charts Not Rendering (INVESTIGATE & FIX)**
- **Problem:** Charts are not appearing on the page
- **Potential Causes:**
  - JavaScript error preventing execution
  - Chart.js not properly loaded
  - Canvas elements not correctly referenced
  - CSS conflicts hiding canvas
- **Action:** Add debugging, error handling, and fix rendering

### **Issue 6: Missing Reflective Orientation Narrative (ADD)**
- **Missing:** 5 language blocks that appear after recommended loads
- **Purpose:** Teach strategy by letting them feel causality, teach BI by letting them see history accumulate
- **Timing:** Only appears AFTER recommended loads are added

---

## Detailed Requirements Analysis

### **Requirement 1: Remove Custom Load Toggle Button**

**Location:** Lines 960-979 (entire custom-load-toggle section)

**Action:** Delete completely:
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

**Also Remove:**
- CSS styles for `.custom-load-toggle`, `.btn-toggle-custom`, `.custom-load-options`, `.custom-options-content`, `.custom-examples`, `.custom-tip`
- JavaScript event listener for `btnToggleCustom`

---

### **Requirement 2: Restructure Story Context Section**

**Current Structure (WRONG):**
```
<div id="storyContext">
  - Story content
  - Custom load form (ALWAYS VISIBLE) ← Problem
  - Recommended loads button
  - Load counter
</div>
```

**New Structure (CORRECT):**
```
<div id="storyContext">
  - Story content
  - Recommended loads button (disabled initially)
  - Load counter
</div>

<!-- NEW: Reflective Narrative (hidden initially) -->
<div id="reflectiveNarrative" class="hidden">
  - 5 language blocks
</div>

<!-- NEW: Custom Load Section (hidden initially) -->
<div id="customLoadSection" class="hidden">
  - "Add Custom Load" button (toggles form)
  - Custom load form (hidden by default)
</div>
```

**Initial States:**
- Story context: `visible` (expanded)
- "Add Recommended Loads" button: `disabled`
- Reflective narrative: `hidden`
- Custom load section: `hidden`
- Custom load form: `collapsed`

**After Recommended Loads Added:**
- Story context: `hidden`
- "Add Recommended Loads" button: `disabled`
- Reflective narrative: `visible` (revealed)
- Custom load section: `visible` (revealed)
- Custom load form: `collapsed`

---

### **Requirement 3: Reflective Orientation Narrative (5 Language Blocks)**

**Location:** New section between story context and custom load section

**Timing:** Only appears AFTER recommended loads are added

**Language Block 1 - Transition from guided to personal:**
```html
<div class="narrative-block">
  <h3>You just saw a small strategic adjustment play out.</h3>
  <p>Nothing dramatic changed. No new markets were added. No major repositioning occurred.</p>
  <p>Just two short local decisions, placed intentionally, and the entire shape of the week shifted.</p>
</div>
```

**Language Block 2 - Prompt reflection, not action:**
```html
<div class="narrative-block">
  <h3>Now pause for a moment.</h3>
  <p>Think about your own operation.</p>
  <p><strong>If you manage carriers, how often do you have the opportunity to step back and ask:</strong></p>
  <ul>
    <li>What patterns am I actually reinforcing?</li>
    <li>Where am I stabilizing, and where am I just reacting?</li>
  </ul>
  <p><strong>If you are a carrier, how often do you get to see:</strong></p>
  <ul>
    <li>Not just what you ran</li>
    <li>But how small changes could have shifted your results?</li>
  </ul>
</div>
```

**Language Block 3 - Invitation to experiment (custom loads):**
```html
<div class="narrative-block">
  <h3>If you'd like, you can now add up to three custom loads.</h3>
  <p>Try modeling something familiar.</p>
  <ul>
    <li>A lane you run often</li>
    <li>A decision you make out of habit</li>
    <li>Or a small adjustment you've wondered about but never tested</li>
  </ul>
  <p>Watch how the report responds.</p>
</div>
```

**Language Block 4 - The business intelligence reveal:**
```html
<div class="narrative-block">
  <h3>This is what business intelligence actually looks like.</h3>
  <p>It's not a static report.</p>
  <p>It's a living history of your decisions, showing you how strategy, consistency, and timing compound over time.</p>
  <p>When you receive these reports, you're not just looking at past performance.</p>
  <p>You're building the ability to think strategically about the future.</p>
</div>
```

**Language Block 5 - Soft conversion (ongoing value):**
```html
<div class="narrative-block">
  <h3>Over time, these reports become more than summaries.</h3>
  <p>They become a record of how your business thinks.</p>
  <ul>
    <li>What you prioritize.</li>
    <li>What you avoid.</li>
    <li>Where you improve.</li>
  </ul>
  <p>That's what turns reporting into real business intelligence.</p>
</div>
```

**Complete HTML Structure:**
```html
<div id="reflectiveNarrative" class="reflective-narrative hidden">
  <div class="narrative-block">
    <h3>You just saw a small strategic adjustment play out.</h3>
    <p>Nothing dramatic changed. No new markets were added. No major repositioning occurred.</p>
    <p>Just two short local decisions, placed intentionally, and the entire shape of the week shifted.</p>
  </div>

  <div class="narrative-block">
    <h3>Now pause for a moment.</h3>
    <p>Think about your own operation.</p>
    <p><strong>If you manage carriers, how often do you have the opportunity to step back and ask:</strong></p>
    <ul>
      <li>What patterns am I actually reinforcing?</li>
      <li>Where am I stabilizing, and where am I just reacting?</li>
    </ul>
    <p><strong>If you are a carrier, how often do you get to see:</strong></p>
    <ul>
      <li>Not just what you ran</li>
      <li>But how small changes could have shifted your results?</li>
    </ul>
  </div>

  <div class="narrative-block">
    <h3>If you'd like, you can now add up to three custom loads.</h3>
    <p>Try modeling something familiar.</p>
    <ul>
      <li>A lane you run often</li>
      <li>A decision you make out of habit</li>
      <li>Or a small adjustment you've wondered about but never tested</li>
    </ul>
    <p>Watch how the report responds.</p>
  </div>

  <div class="narrative-block">
    <h3>This is what business intelligence actually looks like.</h3>
    <p>It's not a static report.</p>
    <p>It's a living history of your decisions, showing you how strategy, consistency, and timing compound over time.</p>
    <p>When you receive these reports, you're not just looking at past performance.</p>
    <p>You're building the ability to think strategically about the future.</p>
  </div>

  <div class="narrative-block">
    <h3>Over time, these reports become more than summaries.</h3>
    <p>They become a record of how your business thinks.</p>
    <ul>
      <li>What you prioritize.</li>
      <li>What you avoid.</li>
      <li>Where you improve.</li>
    </ul>
    <p>That's what turns reporting into real business intelligence.</p>
  </div>
</div>
```

---

### **Requirement 4: Custom Load Section (Hidden Initially)**

**Location:** After reflective narrative section

**Structure:**
```html
<div id="customLoadSection" class="custom-load-section hidden">
  <button id="btnAddCustom" class="btn-add-custom">
    Add Custom Load
    <span class="toggle-icon">▶</span>
  </button>

  <form id="addLoadForm" class="add-load-form collapsed">
    <!-- Existing form fields -->
  </form>
</div>
```

**Behavior:**
- Section initially hidden (`hidden` class)
- Button toggles form visibility (adds/removes `collapsed` class)
- Form initially hidden (`collapsed` class)
- Button icon rotates 90° when active

---

### **Requirement 5: Fix JavaScript Syntax Error**

**Error Location:**
- Line 1577: `const MAX_ADDITIONAL_LOADS = 5;` (keep this one)
- Line 1613: `const MAX_ADDITIONAL_LOADS = 5;` (DELETE this duplicate)

**Action:**
```javascript
// Line 1577 - KEEP
const MAX_ADDITIONAL_LOADS = 5;

// Line 1613 - DELETE
// const MAX_ADDITIONAL_LOADS = 5;  ← Remove this duplicate
```

---

### **Requirement 6: Fix Charts Not Rendering**

**Investigation Steps:**
1. Check browser console for JavaScript errors
2. Verify Chart.js is properly loaded (CDN: https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js)
3. Verify canvas elements exist in HTML
4. Check if chart rendering functions are being called
5. Add debug logging to `renderCharts()` function

**Add Debug Logging:**
```javascript
function renderCharts() {
    console.log('renderCharts called');

    const revenueCtx = document.getElementById('revenueChart');
    const brokerCtx = document.getElementById('brokerChart');
    const deadheadCtx = document.getElementById('deadheadChart');

    console.log('revenueCtx:', revenueCtx);
    console.log('brokerCtx:', brokerCtx);
    console.log('deadheadCtx:', deadheadCtx);

    if (!revenueCtx || !brokerCtx || !deadheadCtx) {
        console.error('One or more canvas elements not found');
        return;
    }

    // ... rest of function
}
```

**Add Error Handling:**
```javascript
try {
    // Chart creation code
} catch (error) {
    console.error('Error rendering charts:', error);
}
```

---

## Implementation Plan

### **Phase 1: Remove Old Code (Lines 960-979 & CSS)**

#### **1.1 Remove Custom Load Toggle HTML**

**Delete lines 960-979:**
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

#### **1.2 Remove Related CSS**

**Delete these CSS rules (search for these selectors):**
```css
.custom-load-toggle { ... }
.btn-toggle-custom { ... }
.btn-toggle-custom:hover { ... }
.btn-toggle-custom.active .toggle-icon { ... }
.toggle-icon { ... }
.custom-load-options { ... }
.custom-load-options.collapsed { ... }
.custom-options-content { ... }
.custom-options-content h4 { ... }
.custom-options-content p { ... }
.custom-examples { ... }
.custom-examples li { ... }
.custom-examples li:before { ... }
.custom-tip { ... }
```

---

### **Phase 2: Restructure Story Context Section (Lines 981-1065)**

#### **2.1 Update Story Context HTML**

**Current structure (lines 981-1065):**
```html
<div id="storyContext" class="story-context visible">
  <button class="btn-close-story" id="btnCloseStory">&times;</button>

  <div class="story-content">
    <!-- 3 content sections -->
  </div>

  <form id="addLoadForm" class="add-load-form">
    <!-- Form fields - WRONG: should be in separate section -->
  </form>

  <div id="recommendedLoadsPlaceholder" class="placeholder">
    <button id="btnAddRecommended" class="btn-recommended disabled" disabled>
      Add Recommended Loads
    </button>
    <p class="btn-info">Reads story above first</p>
  </div>

  <div class="load-counter">
    Added: <span id="loadCount">0</span>/5
    <span class="counter-breakdown">
      (<span id="recommendedCount">0</span> rec + <span id="customCount">0</span> cust)
    </span>
  </div>
</div>
```

**New structure:**
```html
<div id="storyContext" class="story-context visible">
  <button class="btn-close-story" id="btnCloseStory">&times;</button>

  <div class="story-content">
    <!-- 3 content sections remain unchanged -->
  </div>

  <div id="recommendedLoadsPlaceholder" class="placeholder">
    <button id="btnAddRecommended" class="btn-recommended disabled" disabled>
      Add Recommended Loads
    </button>
    <p class="btn-info">Read story above first</p>
  </div>

  <div class="load-counter">
    Added: <span id="loadCount">0</span>/5
    <span class="counter-breakdown">
      (<span id="recommendedCount">0</span> rec + <span id="customCount">0</span> cust)
    </span>
  </div>
</div>
```

**Changes:**
- Removed `<form id="addLoadForm">` block (will move to custom load section)
- Form fields moved to separate custom load section

---

### **Phase 3: Add Reflective Narrative Section**

#### **3.1 Add Reflective Narrative HTML (After storyContext div)**

```html
<div id="reflectiveNarrative" class="reflective-narrative hidden">
  <div class="narrative-block">
    <h3>You just saw a small strategic adjustment play out.</h3>
    <p>Nothing dramatic changed. No new markets were added. No major repositioning occurred.</p>
    <p>Just two short local decisions, placed intentionally, and the entire shape of the week shifted.</p>
  </div>

  <div class="narrative-block">
    <h3>Now pause for a moment.</h3>
    <p>Think about your own operation.</p>
    <p><strong>If you manage carriers, how often do you have the opportunity to step back and ask:</strong></p>
    <ul>
      <li>What patterns am I actually reinforcing?</li>
      <li>Where am I stabilizing, and where am I just reacting?</li>
    </ul>
    <p><strong>If you are a carrier, how often do you get to see:</strong></p>
    <ul>
      <li>Not just what you ran</li>
      <li>But how small changes could have shifted your results?</li>
    </ul>
  </div>

  <div class="narrative-block">
    <h3>If you'd like, you can now add up to three custom loads.</h3>
    <p>Try modeling something familiar.</p>
    <ul>
      <li>A lane you run often</li>
      <li>A decision you make out of habit</li>
      <li>Or a small adjustment you've wondered about but never tested</li>
    </ul>
    <p>Watch how the report responds.</p>
  </div>

  <div class="narrative-block">
    <h3>This is what business intelligence actually looks like.</h3>
    <p>It's not a static report.</p>
    <p>It's a living history of your decisions, showing you how strategy, consistency, and timing compound over time.</p>
    <p>When you receive these reports, you're not just looking at past performance.</p>
    <p>You're building the ability to think strategically about the future.</p>
  </div>

  <div class="narrative-block">
    <h3>Over time, these reports become more than summaries.</h3>
    <p>They become a record of how your business thinks.</p>
    <ul>
      <li>What you prioritize.</li>
      <li>What you avoid.</li>
      <li>Where you improve.</li>
    </ul>
    <p>That's what turns reporting into real business intelligence.</p>
  </div>
</div>
```

---

### **Phase 4: Add Custom Load Section**

#### **4.1 Add Custom Load Section HTML (After reflectiveNarrative div)**

```html
<div id="customLoadSection" class="custom-load-section hidden">
  <button id="btnAddCustom" class="btn-add-custom">
    Add Custom Load
    <span class="toggle-icon">▶</span>
  </button>

  <form id="addLoadForm" class="add-load-form collapsed">
    <div class="form-row">
      <div class="form-group">
        <label>Date</label>
        <input type="date" id="loadDate" min="2026-01-05" max="2026-02-01" required>
        <span class="input-helper">Jan 5 - Feb 1, 2026 only (demo period)</span>
      </div>
      <div class="form-group">
        <label>From Location</label>
        <input type="text" id="fromLocation" placeholder="e.g., Toledo, OH" required>
      </div>
      <div class="form-group">
        <label>To Location</label>
        <input type="text" id="toLocation" placeholder="e.g., Chicago, IL" required>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Paid Miles</label>
        <input type="number" id="paidMiles" min="0" step="0.1" placeholder="245" required>
      </div>
      <div class="form-group">
        <label>Deadhead Miles</label>
        <input type="number" id="deadheadMiles" min="0" step="0.1" placeholder="18" required>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Rate ($)</label>
        <input type="number" id="rate" min="0" step="0.01" placeholder="514.50" required>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Broker Name</label>
        <input type="text" id="brokerName" placeholder="e.g., Alpha" required>
      </div>
    </div>
    <div class="form-actions">
      <button type="submit" id="btnAdd" class="btn-add">Add Load</button>
      <button type="button" id="btnClear" class="btn-clear">Clear Form</button>
    </div>
  </form>
</div>
```

---

### **Phase 5: Add CSS Styles**

#### **5.1 Add Reflective Narrative Styles**

```css
.reflective-narrative {
  background: rgba(59, 130, 246, 0.1);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  padding: 30px;
  margin: 20px 0;
}

.reflective-narrative.hidden {
  display: none;
}

.narrative-block {
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.narrative-block:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.narrative-block h3 {
  color: #3b82f6;
  font-size: 1.3rem;
  margin-bottom: 15px;
}

.narrative-block p {
  color: #e5e7eb;
  line-height: 1.7;
  margin-bottom: 12px;
}

.narrative-block ul {
  list-style: none;
  padding: 0;
  margin: 15px 0;
}

.narrative-block li {
  padding: 10px 0 10px 25px;
  color: #d1d5db;
  border-left: 3px solid #3b82f6;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 0 8px;
}
```

#### **5.2 Add Custom Load Section Styles**

```css
.custom-load-section {
  background: rgba(16, 185, 129, 0.1);
  border: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 12px;
  padding: 30px;
  margin: 20px 0;
}

.custom-load-section.hidden {
  display: none;
}

.btn-add-custom {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
  padding: 14px 30px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-add-custom:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.btn-add-custom .toggle-icon {
  transition: transform 0.3s ease;
}

.btn-add-custom.active .toggle-icon {
  transform: rotate(90deg);
}

.add-load-form.collapsed {
  display: none;
}
```

---

### **Phase 6: Fix JavaScript Syntax Error**

#### **6.1 Remove Duplicate Variable Declaration**

**Line 1613 - DELETE:**
```javascript
const MAX_ADDITIONAL_LOADS = 5;
```

**Keep line 1577:**
```javascript
const MAX_ADDITIONAL_LOADS = 5;
```

---

### **Phase 7: Update JavaScript Functions**

#### **7.1 Update addRecommendedLoads() Function**

**Add reveal logic for narrative and custom section:**

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
    document.getElementById('customCount').textContent = customLoadCount;

    // Check total limit
    if (addedLoadCount >= MAX_ADDITIONAL_LOADS) {
        document.getElementById('btnAdd').disabled = true;
        document.getElementById('btnAddRecommended').disabled = true;
        document.querySelectorAll('.add-load-form input').forEach(input => {
            input.disabled = true;
        });
    }

    // NEW: Hide story context
    document.getElementById('storyContext').classList.add('hidden');

    // NEW: Reveal reflective narrative
    document.getElementById('reflectiveNarrative').classList.remove('hidden');

    // NEW: Reveal custom load section
    document.getElementById('customLoadSection').classList.remove('hidden');

    // NEW: Disable recommended loads button
    document.getElementById('btnAddRecommended').disabled = true;
    document.getElementById('btnAddRecommended').classList.add('disabled');

    // Recalculate everything
    recalculateTotals();
    renderWeeklyTable();
    renderCharts();

    // Clear form
    document.getElementById('addLoadForm').reset();
}
```

#### **7.2 Add Custom Load Toggle Event Listener**

```javascript
// Custom load toggle button
document.getElementById('btnAddCustom').addEventListener('click', function() {
    this.classList.toggle('active');
    const form = document.getElementById('addLoadForm');
    form.classList.toggle('collapsed');
});
```

**Remove old custom load toggle event listener:**
```javascript
// DELETE THIS - old toggle button that was removed
// document.getElementById('btnToggleCustom').addEventListener('click', function() { ... });
```

#### **7.3 Add Debug Logging to renderCharts()**

```javascript
function renderCharts() {
    console.log('renderCharts called');

    const revenueCtx = document.getElementById('revenueChart');
    const brokerCtx = document.getElementById('brokerChart');
    const deadheadCtx = document.getElementById('deadheadChart');

    console.log('revenueCtx:', revenueCtx);
    console.log('brokerCtx:', brokerCtx);
    console.log('deadheadCtx:', deadheadCtx);

    if (!revenueCtx || !brokerCtx || !deadheadCtx) {
        console.error('One or more canvas elements not found');
        return;
    }

    try {
        if (revenueCtx) {
            const weeklyData = window.weeklyData || [];
            const labels = weeklyData.map(w => w.week);
            const revenue = weeklyData.map(w => w.revenue);

            if (revenue.length > 0) {
                new Chart(revenueCtx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Revenue',
                            data: revenue,
                            backgroundColor: 'rgba(59, 130, 246, 0.7)',
                            borderColor: 'rgba(59, 130, 246, 1)',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                labels: { color: '#475569' }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#64748b' },
                                grid: { color: '#e2e8f0' }
                            },
                            x: {
                                ticks: { color: '#64748b' },
                                grid: { color: '#e2e8f0' }
                            }
                        }
                    }
                });
            }
        }

        if (brokerCtx) {
            const brokerData = window.brokerData || {};
            const labels = Object.keys(brokerData);
            const values = Object.values(brokerData);

            if (values.length > 0) {
                new Chart(brokerCtx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: [
                                'rgba(59, 130, 246, 0.7)',
                                'rgba(16, 185, 129, 0.7)',
                                'rgba(245, 158, 11, 0.7)',
                                'rgba(239, 68, 68, 0.7)',
                                'rgba(139, 92, 246, 0.7)'
                            ],
                            borderColor: '#f1f5f9',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                labels: { color: '#475569', font: { size: 12 } },
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        }

        if (deadheadCtx) {
            const deadheadData = window.deadheadData || [];
            const labels = deadheadData.map(w => w.week);
            const deadheadPct = deadheadData.map(w => w.deadhead_percentage);

            if (deadheadPct.length > 0) {
                new Chart(deadheadCtx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Deadhead %',
                            data: deadheadPct,
                            backgroundColor: 'rgba(239, 68, 68, 0.2)',
                            borderColor: 'rgba(239, 68, 68, 1)',
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                labels: { color: '#475569' }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#64748b' },
                                grid: { color: '#e2e8f0' }
                            },
                            x: {
                                ticks: { color: '#64748b' },
                                grid: { color: '#e2e8f0' }
                            }
                        }
                    }
                });
            }
        }

        console.log('Charts rendered successfully');
    } catch (error) {
        console.error('Error rendering charts:', error);
    }
}
```

---

## User Experience Flow

### **Scenario 1: User Arrives at Demo Page**

1. User sees demo page with:
   - "DEMO MODE" banner
   - Story context panel (expanded)
     - "What This Demo Is"
     - "How to Add Loads"
     - "Why Recommended Loads Make Sense"
   - "Add Recommended Loads" button: disabled with "Read story above first"
   - Load counter: "Added: 0/5 (0 rec + 0 cust)"

2. **Nothing else visible yet** - no custom load form, no narrative

---

### **Scenario 2: User Reads Story, Closes It**

1. User reads story content
2. User clicks "×" to close story
3. Story collapses/disappears
4. "Add Recommended Loads" button becomes enabled (purple gradient)

---

### **Scenario 3: User Clicks "Add Recommended Loads"**

1. User clicks purple "Add Recommended Loads" button
2. Both Ohio loads added instantly:
   - Load 1: Columbus → Toledo ($312.40)
   - Load 2: Toledo → Cleveland ($284.60)
3. All metrics update in real-time
4. Charts update (hopefully!)
5. Weekly table shows 2 new rows with "Recommended" badges

**NEW: After recommended loads added:**
6. Story context: hidden
7. "Add Recommended Loads" button: disabled
8. Reflective narrative: **REVEALED** (5 language blocks)
9. Custom load section: **REVEALED** (but form collapsed)
10. Counter: "Added: 2/5 (2 rec + 0 cust)"

---

### **Scenario 4: User Sees Reflective Narrative**

1. User reads 5 language blocks:
   - "You just saw a small strategic adjustment play out"
   - "Now pause for a moment" (reflection prompts)
   - "If you'd like, you can now add up to three custom loads"
   - "This is what business intelligence actually looks like"
   - "Over time, these reports become more than summaries"

2. User understands:
   - They're not being told what to do
   - They're being asked to notice
   - Business intelligence is about seeing causality over time

---

### **Scenario 5: User Clicks "Add Custom Load" Button**

1. User sees green "Add Custom Load" button (now visible after narrative)
2. User clicks button
3. Form expands (collapsible animation)
4. Button icon rotates 90°
5. User sees form fields to enter custom load data

---

### **Scenario 6: User Adds Custom Loads**

1. User enters custom load data
2. User clicks "Add Load" button
3. Custom load added (customLoadCount = 1)
4. Counter: "Added: 3/5 (2 rec + 1 cust)"
5. User can add 2 more custom loads

---

### **Scenario 7: User Adds 3 Custom Loads (Total 5)**

1. User adds 3rd custom load
2. Total count: 5/5 (2 rec + 3 cust)
3. "Add Load" button: disabled
4. Form inputs: disabled
5. All limits enforced

---

## Technical Considerations

### **Progressive Disclosure Architecture**

**Tier 1 - Story Context:**
- Always visible on page load
- Provides orientation without overwhelming
- Must be dismissed before any action

**Tier 2 - Recommended Loads:**
- Revealed after story context dismissed
- Quick win, instant gratification
- Sets baseline for comparison

**Tier 3 - Reflective Narrative:**
- Revealed AFTER recommended loads added
- Only appears when user has seen the system "move"
- Helps interpret what they just experienced
- No commands, only invitations to notice

**Tier 4 - Custom Loads:**
- Revealed AFTER narrative shown
- Allows experimentation with familiar scenarios
- User is now oriented and motivated to explore

### **Key Principles**

1. **Guided → Personal:** Start with curated scenario, then let user explore
2. **Enactment → Orientation:** Let them do, then help them understand
3. **Concrete → Abstract:** Show numbers changing, then teach strategy
4. **Curiosity → Agency:** Use questions, not commands
5. **One Reveal at a Time:** Never overwhelm with all options at once

### **Why This Works Pedagogically**

1. **Teaches strategy by letting them feel causality**
   - User sees 2 loads added → numbers change → narrative helps them feel the impact
   - No explanation until after they've experienced it

2. **Teaches BI by letting them see history accumulate**
   - Narrative shows how small decisions compound over time
   - They're not being taught BI, they're experiencing it

3. **Sells the product by helping them imagine themselves thinking better**
   - No "optimize", no "improve", no "you should"
   - Just clarity about what's possible when you can see causality

---

## File Modification Summary

| Section | Type | Changes | Lines Affected |
|----------|------|-------------|----------------|
| Custom load toggle | HTML | DELETE entire section | 960-979 |
| Custom toggle CSS | CSS | DELETE all styles | ~620-680 |
| Story context | HTML | Remove form, reorder elements | 981-1065 |
| Reflective narrative | HTML | ADD new section with 5 blocks | After storyContext |
| Custom load section | HTML | ADD new section (hidden initially) | After narrative |
| Reflective narrative CSS | CSS | ADD new styles | After existing CSS |
| Custom load section CSS | CSS | ADD new styles | After existing CSS |
| JavaScript variables | JS | DELETE duplicate declaration | 1613 |
| addRecommendedLoads() | JS | ADD reveal logic | ~1771 |
| Custom toggle event | JS | ADD new listener | ~1980 |
| Custom toggle event (old) | JS | DELETE old listener | ~1976 |
| renderCharts() | JS | ADD debug logging | ~1618 |

---

## Testing Checklist

### **Code Changes**
- [ ] Custom load toggle button removed (HTML lines 960-979)
- [ ] Custom load toggle CSS removed (all related styles)
- [ ] Story context form removed from inside storyContext
- [ ] Reflective narrative section added with 5 language blocks
- [ ] Custom load section added (hidden initially)
- [ ] Duplicate MAX_ADDITIONAL_LOADS declaration removed (line 1613)
- [ ] Debug logging added to renderCharts()

### **Functionality**
- [ ] Story context visible on page load
- [ ] Story dismisses when "×" clicked
- [ ] "Add Recommended Loads" button enables after story dismissed
- [ ] Recommended loads add correctly (2 Ohio loads)
- [ ] Story context hides after recommended loads added
- [ ] Reflective narrative reveals after recommended loads added
- [ ] Custom load section reveals after recommended loads added
- [ ] "Add Custom Load" button toggles form visibility
- [ ] Custom load form is hidden by default
- [ ] Custom load form expands when button clicked
- [ ] Custom load limit enforced (max 3)
- [ ] Load counter shows correct breakdown
- [ ] City names display correctly

### **Charts**
- [ ] Chart.js loads without errors
- [ ] Canvas elements are found by renderCharts()
- [ ] Revenue chart renders
- [ ] Broker chart renders
- [ ] Deadhead chart renders
- [ ] Charts update when recommended loads added
- [ ] Charts update when custom loads added
- [ ] No console errors

### **User Experience**
- [ ] Progressive disclosure flow works correctly
- [ ] Only one action available at a time
- [ ] Narrative timing feels natural
- [ ] No overwhelming information
- [ ] Clear visual hierarchy
- [ ] Responsive design works on mobile

---

## Completion Criteria

**Implementation is complete when:**

1. Custom load toggle button removed from page
2. Story context section does NOT contain form fields
3. Reflective narrative section added with 5 language blocks
4. Custom load section added (hidden initially)
5. "Add Custom Load" button toggles form visibility
6. Duplicate MAX_ADDITIONAL_LOADS declaration removed
7. Charts render correctly without errors
8. Recommended loads reveal narrative and custom section
9. User experiences proper progressive disclosure flow
10. All functionality tested and working

---

**This plan is ready for implementation. All requirements have been addressed in detail.**
