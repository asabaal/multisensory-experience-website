# Implementation Plan V4 - Clean Rebuild

## Executive Summary

Complete rebuild of interactive carrier revenue reporting demo from scratch, following authoritative definitions. No refactoring of existing code. Archive previous implementation and implement new, compliant version.

---

## Authoritative Definitions (Fixed)

### Page Identity
- **Type**: Guided, pedagogical, interactive business intelligence demo for carrier revenue reporting
- **Core Purpose**: Teach business strategy by letting users see how specific load decisions change outcomes over time

### Data Definitions

#### Load Record Schema
```javascript
{
    date: "YYYY-MM-DD",
    origin_city: string,
    origin_state: string,
    destination_city: string,
    destination_state: string,
    load_count: 1,
    paid_miles: number,
    deadhead_miles: number,
    revenue: number
}
```

#### Baseline Data
- Curated, static set of baseline loads
- Baseline loads are **immutable**

#### Recommended Loads
- Exactly **two** predefined loads
- Both occur on **2026-01-21**
- Both are **in-state Ohio**

**Load A:**
```javascript
{
    date: "2026-01-21",
    origin_city: "Columbus",
    origin_state: "OH",
    destination_city: "Toledo",
    destination_state: "OH",
    load_count: 1,
    paid_miles: 142,
    deadhead_miles: 8,
    revenue: 312.40
}
```

**Load B:**
```javascript
{
    date: "2026-01-21",
    origin_city: "Toledo",
    origin_state: "OH",
    destination_city: "Cleveland",
    destination_state: "OH",
    load_count: 1,
    paid_miles: 116,
    deadhead_miles: 6,
    revenue: 284.60
}
```

#### Custom Loads
- User may add up to **3** custom loads
- Custom loads follow same schema
- Custom loads are optional

### Behavioral Rules

#### State Model
- Single authoritative in-memory STATE for all loads
- **UI must never be source of truth**

#### Rendering Rules
- All tables, totals, and charts derived from STATE
- Rendering is **deterministic from STATE**
- **No partial or incremental DOM mutation logic**

#### Interaction Rules
- **Add Recommended Loads:**
  - Can be executed **once**
  - Adds exactly the two predefined loads
  - Disables itself after execution

- **Add Custom Load:**
  - Validates inputs
  - Stops accepting loads after 3

- **Interactions may only mutate STATE, then trigger re-render**

#### Pedagogical Narrative Rules
- Narrative text reacts to STATE changes
- Narrative **never mutates data**
- Narrative **never triggers calculations**
- Narrative exists only to help users reflect on what they just saw

### Out of Scope
- Pricing
- Other pages
- Backend persistence
- Authentication
- Optimization
- Additional features

---

## Implementation Plan

### 1. File Strategy

**Action**: Archive existing file, create new file from scratch

- Archive: `/interactive-carrier-revenue-report.html` → `/archive/interactive-carrier-revenue-report.html.old`
- Create: New `/interactive-carrier-revenue-report.html`

**Justification:**
- Complete rebuild ensures compliance with authoritative definitions
- No legacy code contamination
- Clean state model architecture from ground up
- Explicit separation of concerns

---

### 2. State Object Structure

```javascript
const STATE = {
    // Baseline data - IMMUTABLE
    baselineLoads: [
        // 14 baseline loads from Jan 5 - Feb 1, 2026
        // All fields match schema
    ],

    // User-added loads - mutable
    userLoads: [],

    // Load tracking flags
    recommendedLoadsAdded: false,
    customLoadCount: 0,

    // Predefined recommended loads
    recommendedLoads: [
        {
            date: "2026-01-21",
            origin_city: "Columbus",
            origin_state: "OH",
            destination_city: "Toledo",
            destination_state: "OH",
            load_count: 1,
            paid_miles: 142,
            deadhead_miles: 8,
            revenue: 312.40
        },
        {
            date: "2026-01-21",
            origin_city: "Toledo",
            origin_state: "OH",
            destination_city: "Cleveland",
            destination_state: "OH",
            load_count: 1,
            paid_miles: 116,
            deadhead_miles: 6,
            revenue: 284.60
        }
    ],

    // Constraints
    maxCustomLoads: 3,
    totalLoadLimit: 5
};
```

**Key Principle**: STATE is ONLY source of truth

---

### 3. Computation Flow

**All computations are stateless functions - pure functions of STATE**

```javascript
// Get all loads (baseline + user)
function getAllLoads() {
    return [...STATE.baselineLoads, ...STATE.userLoads];
}

// Compute all totals
function computeTotals() {
    const allLoads = getAllLoads();

    const totalRevenue = allLoads.reduce((sum, load) => sum + load.revenue, 0);
    const totalLoads = allLoads.reduce((sum, load) => sum + load.load_count, 0);
    const totalPaidMiles = allLoads.reduce((sum, load) => sum + load.paid_miles, 0);
    const totalDeadheadMiles = allLoads.reduce((sum, load) => sum + load.deadhead_miles, 0);

    const revenuePerMile = totalPaidMiles > 0 ? totalRevenue / totalPaidMiles : 0;
    const deadheadPercentage = totalPaidMiles > 0 ? (totalDeadheadMiles / totalPaidMiles) * 100 : 0;
    const capacityUtilization = (totalLoads / 31) * 100; // 31 days in January
    const revenuePerTotalMile = totalPaidMiles + totalDeadheadMiles > 0
        ? totalRevenue / (totalPaidMiles + totalDeadheadMiles)
        : 0;

    return {
        totalRevenue,
        totalLoads,
        totalPaidMiles,
        totalDeadheadMiles,
        revenuePerMile,
        deadheadPercentage,
        capacityUtilization,
        revenuePerTotalMile
    };
}

// Compute weekly breakdown
function computeWeeklyBreakdown() {
    const allLoads = getAllLoads();
    const weeks = {};

    allLoads.forEach(load => {
        const date = new Date(load.date);
        const weekNumber = getWeekNumber(date);
        const weekKey = weekNumber.toString();

        if (!weeks[weekKey]) {
            weeks[weekKey] = {
                weekNumber,
                weekRange: getWeekRange(weekNumber),
                loads: [],
                revenue: 0,
                paidMiles: 0,
                deadheadMiles: 0,
                loadCount: 0
            };
        }

        weeks[weekKey].loads.push(load);
        weeks[weekKey].revenue += load.revenue;
        weeks[weekKey].paidMiles += load.paid_miles;
        weeks[weekKey].deadheadMiles += load.deadhead_miles;
        weeks[weekKey].loadCount += load.load_count;
    });

    return Object.values(weeks).sort((a, b) => a.weekNumber - b.weekNumber);
}

// Compute lane performance
function computeLanePerformance() {
    const allLoads = getAllLoads();
    const lanes = {};

    allLoads.forEach(load => {
        const laneKey = `${load.origin_city}, ${load.origin_state} → ${load.destination_city}, ${load.destination_state}`;

        if (!lanes[laneKey]) {
            lanes[laneKey] = {
                lane: laneKey,
                loads: [],
                totalRevenue: 0,
                totalMiles: 0,
                loadCount: 0
            };
        }

        lanes[laneKey].loads.push(load);
        lanes[laneKey].totalRevenue += load.revenue;
        lanes[laneKey].totalMiles += load.paid_miles;
        lanes[laneKey].loadCount += load.load_count;
    });

    return Object.values(lanes).map(lane => ({
        lane: lane.lane,
        loads: lane.loadCount,
        totalRevenue: lane.totalRevenue,
        avgRevenuePerLoad: lane.totalRevenue / lane.loadCount,
        totalMiles: lane.totalMiles,
        revenuePerMile: lane.totalRevenue / lane.totalMiles
    }));
}
```

**Computation Rules:**
- No caching of computed values
- Recalculate on every render cycle
- Computation never mutates STATE
- Computation never triggers UI updates

---

### 4. Render Pipeline

**Master render function:**
```javascript
function renderAll() {
    renderSummaryMetrics();
    renderWeeklyTable();
    renderLanePerformanceTable();
    renderCharts();
    renderNarrativeSections();
    updateLoadCounters();
}
```

**Render function pattern:**
```javascript
function renderWeeklyTable() {
    const container = document.getElementById('weeklyTableBody');
    const weeklyData = computeWeeklyBreakdown();

    // FULL DOM REBUILD
    container.innerHTML = '';

    weeklyData.forEach(week => {
        const row = buildWeekRow(week);
        container.appendChild(row);
    });
}
```

**Render Rules:**
- ✅ Full DOM rebuild - clear container, rebuild entirely
- ✅ Deterministic output - same STATE produces identical DOM
- ✅ No incremental updates - never append or toggle classes
- ✅ No side effects - rendering never triggers computations

---

### 5. Interaction Handlers

**Interaction Pattern:**
```
User Action → Validate → Mutate STATE → renderAll()
```

**Handler 1: handleAddRecommendedLoads()**
```javascript
function handleAddRecommendedLoads() {
    if (STATE.recommendedLoadsAdded) {
        return;
    }

    STATE.userLoads.push(...STATE.recommendedLoads);
    STATE.recommendedLoadsAdded = true;

    renderAll();

    const btn = document.getElementById('btnAddRecommended');
    btn.disabled = true;
}
```

**Handler 2: handleAddCustomLoad(formData)**
```javascript
function handleAddCustomLoad(formData) {
    if (STATE.customLoadCount >= STATE.maxCustomLoads) {
        return;
    }

    const newLoad = {
        date: formData.date,
        origin_city: formData.origin_city,
        origin_state: formData.origin_state,
        destination_city: formData.destination_city,
        destination_state: formData.destination_state,
        load_count: 1,
        paid_miles: parseFloat(formData.paid_miles),
        deadhead_miles: parseFloat(formData.deadhead_miles),
        revenue: parseFloat(formData.revenue)
    };

    STATE.userLoads.push(newLoad);
    STATE.customLoadCount++;

    renderAll();

    if (STATE.customLoadCount >= STATE.maxCustomLoads) {
        disableCustomLoadForm();
    }
}
```

**Interaction Rules Compliance:**
- ✅ All interactions mutate STATE first
- ✅ All interactions trigger renderAll() after mutation
- ✅ Recommended loads execute once then disable
- ✅ Custom loads validate before adding
- ✅ Custom loads stop after 3
- ✅ No partial DOM manipulation

---

### 6. Narrative Trigger Points

**Narrative State:**
```javascript
function getNarrativeState() {
    return {
        showStoryContext: !STATE.recommendedLoadsAdded && STATE.userLoads.length === 0,
        showReflectiveNarrative: STATE.recommendedLoadsAdded && STATE.userLoads.length === 2,
        showCustomLoadSection: STATE.recommendedLoadsAdded,
        enableRecommendedButton: true
    };
}
```

**Narrative Rendering:**
```javascript
function renderNarrativeSections() {
    const narrativeState = getNarrativeState();

    const storyContext = document.getElementById('storyContext');
    storyContext.style.display = narrativeState.showStoryContext ? 'block' : 'none';

    const reflectiveNarrative = document.getElementById('reflectiveNarrative');
    reflectiveNarrative.style.display = narrativeState.showReflectiveNarrative ? 'block' : 'none';

    const customLoadSection = document.getElementById('customLoadSection');
    customLoadSection.style.display = narrativeState.showCustomLoadSection ? 'block' : 'none';
}
```

**Narrative Rules Compliance:**
- ✅ Narrative text reacts to STATE changes
- ✅ Narrative never mutates data
- ✅ Narrative never triggers calculations
- ✅ Narrative exists only to help users reflect

---

### 7. Acceptance Checklist

**Functional Requirements:**
- [ ] Baseline loads are immutable (never modified)
- [ ] Recommended loads are exactly two predefined loads
- [ ] Recommended loads can be added once only
- [ ] Recommended button disables after execution
- [ ] Custom loads can be added (up to 3 maximum)
- [ ] Custom load form validates all inputs
- [ ] Custom load form stops accepting after 3 loads
- [ ] All tables display aggregated data from STATE
- [ ] All charts render from computed STATE data
- [ ] Narrative sections show/hide based on STATE

**State Management:**
- [ ] Single STATE object exists as authoritative source
- [ ] UI never serves as source of truth
- [ ] All load data flows through STATE
- [ ] STATE mutations only occur in interaction handlers
- [ ] STATE never mutated by render functions

**Rendering:**
- [ ] All rendering is deterministic from STATE
- [ ] All tables rebuild full DOM on render
- [ ] All charts rebuild from computed data
- [ ] No partial DOM mutation anywhere
- [ ] No incremental DOM updates

**Interaction:**
- [ ] All interactions follow: Validate → Mutate STATE → renderAll()
- [ ] No interaction directly manipulates DOM
- [ ] No interaction triggers calculations outside renderAll()

**Pedagogical:**
- [ ] Story context visible at start
- [ ] Reflective narrative appears after recommended loads
- [ ] Custom load section appears after recommended loads
- [ ] Narrative never modifies data
- [ ] Narrative never triggers calculations

**Out of Scope:**
- [ ] No pricing logic present
- [ ] No backend persistence
- [ ] No authentication
- [ ] No optimization algorithms

**Technical Quality:**
- [ ] Code follows ES6+ conventions
- [ ] No jQuery dependencies
- [ ] Responsive design maintained
- [ ] WCAG 2.1 AA compliance (contrast, alt text, ARIA)
- [ ] Error handling graceful for JS features

---

## Implementation Steps

1. **Archive existing file**
2. **Create new HTML structure**
   - Header, navigation, sections for data display
3. **Implement STATE object**
   - Baseline loads (14 loads from Jan 5 - Feb 1)
   - User loads array (empty initially)
4. **Implement computation functions**
   - getAllLoads(), computeTotals(), computeWeeklyBreakdown(), computeLanePerformance()
5. **Implement render functions**
   - renderAll(), renderSummaryMetrics(), renderWeeklyTable(), renderLanePerformanceTable(), renderCharts(), renderNarrativeSections()
6. **Implement interaction handlers**
   - handleAddRecommendedLoads(), handleAddCustomLoad()
7. **Implement narrative system**
   - Static narrative text that reacts to STATE
8. **Wire up event listeners**
   - Buttons, form submission
9. **Initialize with initial render**
   - renderAll() on page load

---

## File Structure

```
/mnt/storage/repos/multisensory-experience-website/
├── archive/
│   └── interactive-carrier-revenue-report.html.old  (archived)
├── interactive-carrier-revenue-report.html  (NEW - complete rebuild)
└── IMPLEMENTATION_PLAN_V4.md  (this document)
```

---

## Technical Notes

### Baseline Data Source
The baseline loads (14 loads from Jan 5 - Feb 1, 2026) will be extracted from the archived file and hardcoded into STATE.baselineLoads.

### Chart.js Integration
Will use Chart.js (CDN) for rendering:
- Weekly Revenue (bar chart)
- Broker Distribution (pie chart)
- Deadhead Percentage (line chart)

### Responsive Design
- Mobile-first approach
- Tables scrollable on small screens
- Flexbox/Grid layouts

### Accessibility
- WCAG 2.1 AA compliance
- Proper contrast ratios
- Alt text for images
- ARIA labels where needed
- Keyboard navigation support
