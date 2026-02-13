# Visual Database Technical Implementation Requirements

## Executive Summary

This document provides complete technical specifications for implementing a zero-dependency visual database system using vanilla JavaScript, HTML, and CSS. The system features a three-panel interface (filters sidebar, scrollable table, detail panel) with dynamic data loading from CSV files, optional JSON for related data attachments, and real-time filtering/sorting capabilities.

## System Architecture Overview

### Core Components

1. **Data Layer** - CSV/JSON file loading and parsing
2. **Data Normalization Module** - Data transformation and relationship mapping
3. **Rendering Module** - Dynamic UI generation (filters, table, detail panel)
4. **Application Module** - State management and orchestration

### Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Flexbox layout, CSS variables, transitions
- **Vanilla JavaScript (ES6+)** - No frameworks or libraries
- **Fetch API** - Data loading
- **DOM API** - Dynamic content creation

### Browser Requirements

- Modern browser with ES6 support
- Fetch API support
- Flexbox CSS support
- CSS Variables support

---

## Data Layer Specifications

### Required File Structure

```
project/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── data-ingestion.js
│   ├── data-normalization.js
│   ├── renderer.js
│   └── app.js
└── data/
    ├── content.csv (REQUIRED)
    └── media.json (OPTIONAL - for related data attachments)
```

### CSV File Specifications

#### Format Requirements

- File format: UTF-8 encoded CSV
- Line endings: LF (Unix-style) or CRLF (Windows-style)
- Field delimiter: Comma (`,`)
- Text qualifier: Double quotes (`"`)
- Header row: Required, must be first row
- Column headers: Must be present on row 1

#### Header Row Format

```csv
identifier_column,column_name_1,column_name_2,optional_column,...
```

**Requirements:**
- Must contain at least one column to use as unique identifier
- Column names become object properties in JavaScript
- No duplicate column names allowed
- Spaces in column names are preserved

#### Data Row Format

```csv
ID-001,value1,value2,value3
ID-002,value1,value2,value3
```

**Requirements:**
- Each row represents one database entry
- Number of values must match number of columns in header
- Values may be enclosed in double quotes if they contain commas or quotes
- Empty values are allowed (represented as empty string or `,,`)

#### Quoted Field Handling

**Rules:**
1. Fields containing commas must be enclosed in double quotes
2. Fields containing double quotes must escape them with two double quotes (`""`)
3. Empty fields can be represented as `""` or nothing between delimiters

**Examples:**
```csv
ID,Title,Description
1,"Simple Title",No issues
2,"Title, With, Commas","Description with ""quotes"" inside"
3,"",Empty title
4,"Another Title","Description
with
line
breaks"
```

**CSV Parsing Algorithm Requirements:**

```javascript
// PSEUDOCODE - Actual implementation required
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current);
    return result;
}
```

#### Date Column Specifications

**Supported Formats:**
- ISO 8601: `2025-10-03`
- US Format: `10/3/2025` or `10/03/2025`
- With time: `2025-10-03T14:30:00Z`
- Text: Can be parsed by JavaScript `Date()` constructor

**Normalization Required:**
- Convert all valid dates to ISO 8601 format (YYYY-MM-DD)
- Invalid dates should remain as original string
- Empty dates should remain as empty string

### JSON File Specifications (Optional)

#### Purpose
Store related data attachments (one-to-many relationship) linked to CSV entries by identifier.

#### File Format

```json
[
  {
    "content_id": "ID-001",
    "type": "video|audio|image",
    "source": "local|remote",
    "path": "relative/path/to/file.ext",
    "url": "https://remote-url.com/file.ext",
    "display": "embed|link"
  }
]
```

#### Schema

**Required Fields:**
- `content_id` (string) - Must match identifier column in CSV
- `type` (string) - One of: "video", "audio", "image"
- `source` (string) - One of: "local", "remote"

**Conditional Fields:**
- `path` (string, required if source="local") - Relative path to file
- `url` (string, required if source="remote") - Full URL to remote resource
- `display` (string, optional, default="link") - One of: "embed", "link"

#### Relationship Mapping

- One CSV entry can have multiple JSON records
- Link field: JSON record's `content_id` must match CSV row's identifier
- If no matching JSON records, entry has empty attachments array

---

## Data Ingestion Module Specifications

### Module Purpose
Load CSV and optional JSON files from server, handle protocol validation, parse CSV into structured data.

### Module Structure

```javascript
const DataIngestion = {
    // Methods documented below
};
```

### Required Methods

#### 1. `checkProtocol()`

**Purpose:** Validate that application is running via HTTP server, not file:// protocol.

**Implementation:**

```javascript
checkProtocol() {
    if (window.location.protocol === 'file:') {
        throw new Error('file:// protocol detected');
    }
}
```

**Usage:**
- Call at start of all data loading methods
- Throws error if file:// detected
- Browser blocks fetch() on file:// for security reasons

**Error Handling:**
- Catch error in calling code
- Display user-friendly message requiring HTTP server
- Suggest running: `python3 -m http.server` or `npx http-server`

#### 2. `loadCSVFiles(dataPath = 'data/')`

**Purpose:** Load and parse CSV file containing primary data.

**Parameters:**
- `dataPath` (string, optional, default='data/') - Relative path to data directory

**Return Type:** `Promise<Array<Object>>` - Array of parsed row objects

**Implementation Steps:**

1. Call `checkProtocol()` to validate protocol
2. Construct fetch URL: `${dataPath}content.csv`
3. Execute fetch request
4. Check response.ok (HTTP status 200-299)
5. Get response text
6. Parse CSV text using parseCSV() method
7. Return parsed rows array

**Error Cases:**

| Error Type | HTTP Status | Action |
|------------|--------------|--------|
| File not found | 404 | Throw error with filename |
| Server error | 5xx | Throw error with status |
| Network error | N/A | Throw error with message |
| Protocol error | N/A | Throw 'file:// protocol detected' |

**Implementation Template:**

```javascript
async loadCSVFiles(dataPath = 'data/') {
    try {
        this.checkProtocol();

        const response = await fetch(`${dataPath}content.csv`);
        if (!response.ok) {
            throw new Error(`Failed to load content.csv: ${response.statusText}`);
        }
        const csvText = await response.text();
        return this.parseCSV(csvText);
    } catch (error) {
        console.error('Error loading CSV file:', error);
        throw error;
    }
}
```

#### 3. `loadMediaJSON(dataPath = 'data/')`

**Purpose:** Load optional JSON file containing related media attachments.

**Parameters:**
- `dataPath` (string, optional, default='data/') - Relative path to data directory

**Return Type:** `Promise<Array<Object>>` - Array of media record objects

**Implementation Steps:**

1. Call `checkProtocol()` to validate protocol
2. Construct fetch URL: `${dataPath}media.json`
3. Execute fetch request
4. If response.status === 404, return empty array (file is optional)
5. If other error, throw error
6. Parse JSON response
7. Return parsed array

**Implementation Template:**

```javascript
async loadMediaJSON(dataPath = 'data/') {
    try {
        this.checkProtocol();

        const response = await fetch(`${dataPath}media.json`);
        if (!response.ok) {
            if (response.status === 404) {
                return []; // File is optional
            }
            throw new Error(`Failed to load media.json: ${response.statusText}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        if (error.message && error.message.includes('404')) {
            return [];
        }
        console.error('Error loading media.json:', error);
        throw error;
    }
}
```

#### 4. `parseCSV(csvText)`

**Purpose:** Parse CSV text string into array of row objects.

**Parameters:**
- `csvText` (string) - Raw CSV file content

**Return Type:** `Array<Object>` - Array of row objects, where each key is column header

**Implementation Steps:**

1. Trim csvText (remove leading/trailing whitespace)
2. Split by newline characters (`\n`)
3. Check if lines.length < 2, return empty array
4. Parse first line as headers using parseCSVLine()
5. For each subsequent line:
   - Parse line using parseCSVLine()
   - Check if values.length === headers.length
   - If match, create object mapping headers to values
   - Trim each value, replace empty strings with ''
   - Add object to rows array
6. Return rows array

**Implementation Template:**

```javascript
parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    if (lines.length < 2) {
        return [];
    }

    const headers = lines[0].split(',').map(h => h.trim());
    const rows = [];

    for (let i = 1; i < lines.length; i++) {
        const values = this.parseCSVLine(lines[i]);
        if (values.length === headers.length) {
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] ? values[index].trim() : '';
            });
            rows.push(row);
        }
    }

    return rows;
}
```

#### 5. `parseCSVLine(line)`

**Purpose:** Parse a single CSV line into array of values, handling quoted fields correctly.

**Parameters:**
- `line` (string) - Single line from CSV file (not including newline)

**Return Type:** `Array<string>` - Array of field values

**Implementation Steps:**

1. Initialize result array, current string, inQuotes boolean
2. Iterate through each character in line:
   - If character is `"`, toggle inQuotes boolean
   - If character is `,` and not inQuotes:
     - Push current to result array
     - Reset current to empty string
   - Otherwise, append character to current
3. After loop, push final current value to result
4. Return result array

**Implementation Template:**

```javascript
parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current);
    return result;
}
```

---

## Data Normalization Module Specifications

### Module Purpose
Transform raw CSV data into normalized objects, attach related media, extract filter options.

### Module Structure

```javascript
const DataNormalization = {
    // Methods documented below
};
```

### Required Methods

#### 1. `normalizeRows(rawRows)`

**Purpose:** Transform array of raw CSV row objects into normalized entry objects.

**Parameters:**
- `rawRows` (Array<Object>) - Array of raw row objects from CSV parser

**Return Type:** `Array<Object>` - Array of normalized entry objects

**Implementation Steps:**

1. Map over rawRows array
2. For each row, call normalizeRow(row)
3. Return array of normalized objects

**Implementation Template:**

```javascript
normalizeRows(rawRows) {
    return rawRows.map(row => this.normalizeRow(row));
}
```

#### 2. `normalizeRow(rawRow)`

**Purpose:** Transform single raw CSV row into normalized entry object with property mapping.

**Parameters:**
- `rawRow` (Object) - Single raw row object from CSV parser

**Return Type:** `Object` - Normalized entry object

**Mapping Requirements:**

You MUST create a property mapping specific to your CSV structure. Example:

```javascript
normalizeRow(rawRow) {
    return {
        // Unique identifier - REQUIRED
        contentId: rawRow['content_id'] || '',

        // Date fields - normalize to ISO format
        releaseDate: this.normalizeDate(rawRow['Release Date'] || ''),

        // Text/categorical fields
        showType: rawRow['Show/Content Type'] || rawRow['Show or Content Type'] || '',
        season: rawRow['Season'] || '',
        episode: rawRow['Episode'] || '',
        month: rawRow['Month'] || '',
        weekOf: this.normalizeDate(rawRow['Week of x'] || rawRow['Week Of'] || ''),

        // Media source
        mediaSource: rawRow['Media Source'] || '',

        // Array for related media attachments (populated later)
        attachedMedia: []
    };
}
```

**Mapping Rules:**
- Map CSV column names to camelCase property names
- Handle multiple possible column names (e.g., `Show/Content Type` OR `Show or Content Type`)
- Fallback to empty string if field missing
- Include `attachedMedia: []` array for linking to JSON data
- Call normalizeDate() for all date fields

#### 3. `normalizeDate(dateString)`

**Purpose:** Convert date string to ISO 8601 format if valid, otherwise return original string.

**Parameters:**
- `dateString` (string) - Date string from CSV

**Return Type:** `string` - ISO format date (YYYY-MM-DD) or original string if invalid/empty

**Implementation Steps:**

1. If dateString is falsy or empty string, return ''
2. Create Date object: `new Date(dateString)`
3. Check if date is invalid: `isNaN(date.getTime())`
4. If invalid, return original dateString
5. If valid, convert to ISO format: `date.toISOString().split('T')[0]`
6. Return formatted string

**Implementation Template:**

```javascript
normalizeDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;

    return date.toISOString().split('T')[0];
}
```

#### 4. `attachMedia(entries, mediaRecords)`

**Purpose:** Link media records from JSON to corresponding entries by content identifier.

**Parameters:**
- `entries` (Array<Object>) - Array of normalized entry objects
- `mediaRecords` (Array<Object>) - Array of media record objects from JSON

**Return Type:** `undefined` - Modifies entries array in place

**Implementation Steps:**

1. Create empty mediaMap object
2. Iterate through mediaRecords:
   - Extract contentId from record
   - If mediaMap doesn't have key for contentId, create empty array
   - Push record to mediaMap[contentId]
3. Iterate through entries:
   - Check if mediaMap has entry's contentId as key
   - If yes, set entry.attachedMedia = mediaMap[contentId]
   - If no, entry.attachedMedia remains empty array (already initialized)

**Implementation Template:**

```javascript
attachMedia(entries, mediaRecords) {
    const mediaMap = {};

    mediaRecords.forEach(record => {
        const contentId = record.content_id;
        if (!mediaMap[contentId]) {
            mediaMap[contentId] = [];
        }
        mediaMap[contentId].push(record);
    });

    entries.forEach(entry => {
        if (mediaMap[entry.contentId]) {
            entry.attachedMedia = mediaMap[entry.contentId];
        }
    });
}
```

#### 5. `extractFilterOptions(entries)`

**Purpose:** Extract unique values from entries for building filter dropdown options.

**Parameters:**
- `entries` (Array<Object>) - Array of normalized entry objects

**Return Type:** `Object` - Object where keys are field names, values are sorted arrays of unique values

**Implementation Steps:**

1. Create empty options object
2. Iterate through each entry:
   - Iterate through each key in entry:
     - Skip if key is 'contentId' or 'attachedMedia' (internal fields)
     - Get value: entry[key]
     - If value is truthy and not empty string:
       - If options[key] doesn't exist, create new Set
       - Add value to options[key] Set
3. After processing all entries, convert Sets to sorted arrays:
   - Iterate through keys in options
   - Convert options[key] to array: `Array.from(options[key])`
   - Sort array alphabetically
4. Return options object

**Implementation Template:**

```javascript
extractFilterOptions(entries) {
    const options = {};

    entries.forEach(entry => {
        Object.keys(entry).forEach(key => {
            if (key === 'contentId' || key === 'attachedMedia') return;

            const value = entry[key];
            if (value && value !== '') {
                if (!options[key]) {
                    options[key] = new Set();
                }
                options[key].add(value);
            }
        });
    });

    Object.keys(options).forEach(key => {
        options[key] = Array.from(options[key]).sort();
    });

    return options;
}
```

---

## Rendering Module Specifications

### Module Purpose
Generate all UI components dynamically: filter dropdowns, table with rows, detail panel, media elements.

### Module Structure

```javascript
const Renderer = {
    // Configuration arrays and methods documented below
};
```

### Configuration Arrays (Customizable)

#### Month Names Array (Optional)

```javascript
monthNames: ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
```

**Purpose:** Convert month numbers to names (1 → January)

#### Month Colors Array (Optional)

```javascript
monthColors: [
    'rgba(255, 182, 193, 0.15)',   // January
    'rgba(173, 216, 230, 0.15)',   // February
    'rgba(144, 238, 144, 0.15)',   // March
    'rgba(255, 218, 185, 0.15)',   // April
    'rgba(221, 160, 221, 0.15)',   // May
    'rgba(255, 255, 153, 0.15)',   // June
    'rgba(255, 160, 122, 0.15)',   // July
    'rgba(250, 128, 114, 0.12)',   // August
    'rgba(216, 191, 216, 0.15)',   // September
    'rgba(255, 200, 150, 0.15)',   // October
    'rgba(176, 224, 230, 0.15)',   // November
    'rgba(255, 228, 225, 0.15)'    // December
]
```

**Purpose:** Background colors for month-based cells

### Required Methods

#### 1. `renderFilterUI(filterOptions, onFilterChange)`

**Purpose:** Generate filter dropdown interface based on available field values.

**Parameters:**
- `filterOptions` (Object) - Filter options object from extractFilterOptions()
- `onFilterChange` (Function) - Callback function to execute when filter changes

**Return Type:** `undefined` - Directly modifies DOM

**DOM Manipulation Steps:**

1. Get container element: `document.getElementById('filter-container')`
2. Clear container innerHTML
3. Iterate through keys in filterOptions:
   - For each key:
     - Create filter-group div element
     - Create label element with formatted field name
     - Create select element with ID `filter-${key}`
     - Add "All" option (value='', text='All')
     - For each value in filterOptions[key]:
       - Create option element
       - Set value and textContent
       - Append to select
     - Add change event listener calling onFilterChange()
     - Assemble and append to container
4. All filter groups appended to container

**Implementation Template:**

```javascript
renderFilterUI(filterOptions, onFilterChange) {
    const container = document.getElementById('filter-container');
    container.innerHTML = '';

    Object.keys(filterOptions).forEach(key => {
        const group = document.createElement('div');
        group.className = 'filter-group';

        const label = document.createElement('label');
        label.textContent = this.formatFilterLabel(key);
        group.appendChild(label);

        const select = document.createElement('select');
        select.id = `filter-${key}`;

        const allOption = document.createElement('option');
        allOption.value = '';
        allOption.textContent = 'All';
        select.appendChild(allOption);

        filterOptions[key].forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        });

        select.addEventListener('change', () => onFilterChange());
        group.appendChild(select);

        container.appendChild(group);
    });
}
```

#### 2. `formatFilterLabel(key)`

**Purpose:** Convert camelCase property names to human-readable labels.

**Parameters:**
- `key` (string) - Property name from entry object

**Return Type:** `string` - Formatted human-readable label

**Transformation Rules:**
1. Capitalize first letter
2. Insert space before uppercase letters
3. Example: 'releaseDate' → 'Release Date'

**Implementation Template:**

```javascript
formatFilterLabel(key) {
    return key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
}
```

#### 3. `renderContentList(entries, onSelectEntry)`

**Purpose:** Render table containing all filtered entries.

**Parameters:**
- `entries` (Array<Object>) - Array of entry objects to display
- `onSelectEntry` (Function) - Callback function to execute when row clicked

**Return Type:** `undefined` - Directly modifies DOM

**DOM Manipulation Steps:**

1. Get container element: `document.getElementById('content-list')`
2. Clear container innerHTML
3. Check if entries.length === 0:
   - Set innerHTML to 'no-content' div with message
   - Return early
4. Create table element with class 'content-table'
5. Create thead element
6. Create header row tr element
7. For each column in your table:
   - Create th element with column name
   - Set dataset.columnIndex for sorting (optional)
   - Append to header row
8. Append header row to thead
9. Append thead to table
10. Create tbody element
11. For each entry in entries:
    - Call createTableRow(entry, onSelectEntry)
    - Append returned row to tbody
12. Append tbody to table
13. Append table to container

**Column Selection:**

You MUST define which fields to display in table. Example:

```javascript
const headers = ['Release Date', 'Show Type', 'Season', 'Episode', 'Month'];
```

**Implementation Template:**

```javascript
renderContentList(entries, onSelectEntry) {
    const container = document.getElementById('content-list');
    container.innerHTML = '';

    if (entries.length === 0) {
        container.innerHTML = '<div class="no-content">No content entries found</div>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'content-table';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    const headers = ['Release Date', 'Show Type', 'Season', 'Episode', 'Month'];
    headers.forEach((header, index) => {
        const th = document.createElement('th');
        th.textContent = header;
        th.dataset.columnIndex = index;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    entries.forEach(entry => {
        const row = this.createTableRow(entry, onSelectEntry);
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    container.appendChild(table);
}
```

#### 4. `createTableRow(entry, onSelectEntry)`

**Purpose:** Create single table row with cells populated from entry data.

**Parameters:**
- `entry` (Object) - Entry object to render
- `onSelectEntry` (Function) - Callback for click event

**Return Type:** `HTMLElement` - tr element with td children

**Implementation Steps:**

1. Create tr element with class 'table-row'
2. Set dataset.id to entry's unique identifier
3. For each column in your table:
   - Call createTableCell() with appropriate field value
   - Optionally apply background color to cell based on value
   - Append cell to row
4. Add click event listener calling onSelectEntry(entry)
5. Return tr element

**Cell Creation Pattern:**

```javascript
// Example cell creation with optional color coding
tr.appendChild(this.createTableCell(entry.releaseDate || '-'));

const showCell = this.createTableCell(entry.showType || 'Untitled');
if (entry.showType) {
    const showColor = this.getShowColor(entry.showType);
    showCell.style.backgroundColor = showColor;
}
tr.appendChild(showCell);
```

**Implementation Template:**

```javascript
createTableRow(entry, onSelectEntry) {
    const tr = document.createElement('tr');
    tr.className = 'table-row';
    tr.dataset.id = entry.contentId;

    tr.appendChild(this.createTableCell(entry.releaseDate || '-'));

    const showCell = this.createTableCell(entry.showType || 'Untitled');
    if (entry.showType) {
        const showColor = this.getShowColor(entry.showType);
        showCell.style.backgroundColor = showColor;
    }
    tr.appendChild(showCell);

    tr.appendChild(this.createTableCell(entry.season || '-'));
    tr.appendChild(this.createTableCell(entry.episode || '-'));

    const monthCell = this.createTableCell(this.getMonthName(entry.month));
    const monthColor = this.getMonthColor(entry.month);
    if (monthColor) {
        monthCell.style.backgroundColor = monthColor;
    }
    tr.appendChild(monthCell);

    tr.addEventListener('click', () => onSelectEntry(entry));

    return tr;
}
```

#### 5. `createTableCell(text)`

**Purpose:** Create single table cell with text content.

**Parameters:**
- `text` (string) - Cell content

**Return Type:** `HTMLElement` - td element

**Implementation Template:**

```javascript
createTableCell(text) {
    const td = document.createElement('td');
    td.textContent = text;
    return td;
}
```

#### 6. `renderDetailsPanel(entry)`

**Purpose:** Render detail panel showing all information about selected entry.

**Parameters:**
- `entry` (Object) - Selected entry object

**Return Type:** `undefined` - Directly modifies DOM

**DOM Manipulation Steps:**

1. Get panel element: `document.getElementById('details-panel')`
2. Get title element: `document.getElementById('details-title')`
3. Get content element: `document.getElementById('details-content')`
4. Set title textContent to entry's display field
5. Clear content element innerHTML
6. Call createDetailItem() for each field to display:
   - Create detail item div
   - Append to content element
7. Call renderAttachedMedia(entry) to show media attachments
8. Remove 'hidden' class from panel

**Field Display Pattern:**

```javascript
// Show unique identifier
if (entry.contentId) {
    content.appendChild(this.createDetailItem('Content ID', entry.contentId));
}

// Display key-value pairs
const fields = [
    { key: 'releaseDate', label: 'Release Date' },
    { key: 'season', label: 'Season' },
    { key: 'episode', label: 'Episode' },
    // ... more fields
];

fields.forEach(field => {
    if (entry[field.key] && entry[field.key] !== '') {
        content.appendChild(this.createDetailItem(field.label, entry[field.key]));
    }
});
```

**Implementation Template:**

```javascript
renderDetailsPanel(entry) {
    const panel = document.getElementById('details-panel');
    const title = document.getElementById('details-title');
    const content = document.getElementById('details-content');

    title.textContent = entry.showType || 'Untitled';
    content.innerHTML = '';

    if (entry.contentId) {
        content.appendChild(this.createDetailItem('Content ID', entry.contentId));
    }

    const fields = [
        { key: 'releaseDate', label: 'Release Date' },
        { key: 'weekOf', label: 'Week Of' },
        { key: 'month', label: 'Month' },
        { key: 'season', label: 'Season' },
        { key: 'episode', label: 'Episode' },
        { key: 'mediaSource', label: 'Media Source' }
    ];

    fields.forEach(field => {
        if (entry[field.key] && entry[field.key] !== '') {
            content.appendChild(this.createDetailItem(field.label, entry[field.key]));
        }
    });

    this.renderAttachedMedia(entry);

    panel.classList.remove('hidden');
}
```

#### 7. `createDetailItem(label, value)`

**Purpose:** Create detail panel item showing label-value pair.

**Parameters:**
- `label` (string) - Field label
- `value` (string) - Field value

**Return Type:** `HTMLElement` - div element with label and value

**DOM Structure:**

```html
<div class="detail-item">
    <div class="detail-label">LABEL</div>
    <div class="detail-value">VALUE</div>
</div>
```

**Implementation Template:**

```javascript
createDetailItem(label, value) {
    const div = document.createElement('div');
    div.className = 'detail-item';

    const labelEl = document.createElement('div');
    labelEl.className = 'detail-label';
    labelEl.textContent = label;
    div.appendChild(labelEl);

    const valueEl = document.createElement('div');
    valueEl.className = 'detail-value';
    valueEl.textContent = value;
    div.appendChild(valueEl);

    return div;
}
```

#### 8. `renderAttachedMedia(entry)`

**Purpose:** Render media attachments in detail panel.

**Parameters:**
- `entry` (Object) - Selected entry object

**Return Type:** `undefined` - Directly modifies DOM

**Implementation Steps:**

1. Get container element: `document.getElementById('attached-content-items')`
2. Check if entry.attachedMedia exists and has length > 0:
   - If yes:
     - Clear container innerHTML
     - For each media in entry.attachedMedia:
       - Call createMediaElement(media)
       - Append to container
   - If no:
     - Set innerHTML to 'no-content' div with message

**Implementation Template:**

```javascript
renderAttachedMedia(entry) {
    const container = document.getElementById('attached-content-items');

    if (entry.attachedMedia && entry.attachedMedia.length > 0) {
        container.innerHTML = '';
        entry.attachedMedia.forEach(media => {
            const mediaEl = this.createMediaElement(media);
            container.appendChild(mediaEl);
        });
    } else {
        container.innerHTML = '<div class="no-content">No media attached yet.</div>';
    }
}
```

#### 9. `createMediaElement(media)`

**Purpose:** Create media element wrapper based on media type and source.

**Parameters:**
- `media` (Object) - Media record with type, source, path/url, display

**Return Type:** `HTMLElement` - Wrapper div containing media element or link

**DOM Structure:**

```html
<div class="media-wrapper">
    <div class="media-type-label">TYPE - SOURCE</div>
    <!-- Media element or link here -->
</div>
```

**Implementation Steps:**

1. Create wrapper div with class 'media-wrapper'
2. Create type label div with class 'media-type-label'
3. Set textContent: `${media.type.toUpperCase()} - ${media.source.toUpperCase()}`
4. Append label to wrapper
5. Check media.source:
   - If 'local':
     - Call createLocalMedia(media)
     - Append result to wrapper
   - If 'remote':
     - Check media.display (or default to 'link')
     - If 'embed':
       - Call createRemoteEmbed(media)
       - If result exists, append to wrapper
       - Otherwise, call createRemoteLink(media) and append
     - If 'link':
       - Call createRemoteLink(media) and append
6. Return wrapper

**Implementation Template:**

```javascript
createMediaElement(media) {
    const wrapper = document.createElement('div');
    wrapper.className = 'media-wrapper';

    const typeLabel = document.createElement('div');
    typeLabel.className = 'media-type-label';
    typeLabel.textContent = `${media.type.toUpperCase()} - ${media.source.toUpperCase()}`;
    wrapper.appendChild(typeLabel);

    if (media.source === 'local') {
        const element = this.createLocalMedia(media);
        wrapper.appendChild(element);
    } else if (media.source === 'remote') {
        const display = media.display || 'link';
        if (display === 'embed') {
            const element = this.createRemoteEmbed(media);
            if (element) {
                wrapper.appendChild(element);
            } else {
                wrapper.appendChild(this.createRemoteLink(media));
            }
        } else {
            wrapper.appendChild(this.createRemoteLink(media));
        }
    }

    return wrapper;
}
```

#### 10. `createLocalMedia(media)`

**Purpose:** Create HTML5 media element for local file.

**Parameters:**
- `media` (Object) - Media record with type and path

**Return Type:** `HTMLElement` - video, audio, or img element

**Implementation by Type:**

**Video:**
- Create video element with controls attribute
- Set width: '100%', maxHeight: '300px', borderRadius: '8px'
- Create source element with src=media.path, type='video/mp4'
- Append source to video
- Return video

**Audio:**
- Create audio element with controls attribute
- Set width: '100%'
- Create source element with src=media.path
- Append source to audio
- Return audio

**Image:**
- Create img element with src=media.path
- Set width: '100%', maxHeight: '300px', borderRadius: '8px', objectFit: 'contain'
- Return img

**Implementation Template:**

```javascript
createLocalMedia(media) {
    const path = `media/${media.path}`;

    if (media.type === 'video') {
        const video = document.createElement('video');
        video.controls = true;
        video.style.width = '100%';
        video.style.maxHeight = '300px';
        video.style.borderRadius = '8px';
        const source = document.createElement('source');
        source.src = path;
        source.type = 'video/mp4';
        video.appendChild(source);
        return video;
    } else if (media.type === 'audio') {
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.style.width = '100%';
        const source = document.createElement('source');
        source.src = path;
        audio.appendChild(source);
        return audio;
    } else if (media.type === 'image') {
        const img = document.createElement('img');
        img.src = path;
        img.style.width = '100%';
        img.style.maxHeight = '300px';
        img.style.borderRadius = '8px';
        img.style.objectFit = 'contain';
        return img;
    }
}
```

#### 11. `createRemoteEmbed(media)`

**Purpose:** Create embedded HTML5 media element for remote URL.

**Parameters:**
- `media` (Object) - Media record with type and url

**Return Type:** `HTMLElement|null` - video, audio element, or null if not embeddable

**Implementation Template:**

```javascript
createRemoteEmbed(media) {
    if (media.type === 'video') {
        const video = document.createElement('video');
        video.controls = true;
        video.style.width = '100%';
        video.style.maxHeight = '300px';
        video.style.borderRadius = '8px';
        const source = document.createElement('source');
        source.src = media.url;
        source.type = 'video/mp4';
        video.appendChild(source);
        return video;
    } else if (media.type === 'audio') {
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.style.width = '100%';
        const source = document.createElement('source');
        source.src = media.url;
        audio.appendChild(source);
        return audio;
    }
    return null;
}
```

#### 12. `createRemoteLink(media)`

**Purpose:** Create clickable link to remote media file.

**Parameters:**
- `media` (Object) - Media record with type and url

**Return Type:** `HTMLElement` - anchor element

**DOM Structure:**

```html
<a href="URL" target="_blank" rel="noopener noreferrer" class="media-link">
    <span class="media-link-icon">🔗</span>
    <span class="media-link-text">View TYPE (external)</span>
</a>
```

**Implementation Template:**

```javascript
createRemoteLink(media) {
    const link = document.createElement('a');
    link.href = media.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'media-link';
    link.innerHTML = `
        <span class="media-link-icon">🔗</span>
        <span class="media-link-text">View ${media.type} (external)</span>
    `;
    return link;
}
```

#### 13. `hideDetailsPanel()`

**Purpose:** Hide detail panel by adding 'hidden' class.

**Return Type:** `undefined` - Directly modifies DOM

**Implementation Template:**

```javascript
hideDetailsPanel() {
    const panel = document.getElementById('details-panel');
    panel.classList.add('hidden');
}
```

#### 14. `highlightSelectedEntry(entryId)`

**Purpose:** Highlight selected row in table and scroll into view.

**Parameters:**
- `entryId` (string|null) - Unique identifier of selected entry

**Return Type:** `undefined` - Directly modifies DOM

**Implementation Steps:**

1. Select all elements with class 'table-row'
2. Remove 'selected' class from all rows
3. If entryId is truthy:
   - Find element with dataset.id matching entryId
   - If found:
     - Add 'selected' class
     - Scroll element into view with smooth behavior, block: 'center'

**Implementation Template:**

```javascript
highlightSelectedEntry(entryId) {
    document.querySelectorAll('.table-row').forEach(el => {
        el.classList.remove('selected');
    });

    if (entryId) {
        const selected = document.querySelector(`[data-id="${entryId}"]`);
        if (selected) {
            selected.classList.add('selected');
            selected.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}
```

---

## Application Module Specifications

### Module Purpose
Orchestrate entire application, manage state, handle events, coordinate between modules.

### Module Structure

```javascript
const App = {
    // State properties and methods documented below
};
```

### State Properties

```javascript
entries: [],           // Array of all loaded entries (from CSV)
filteredEntries: [],   // Array of currently filtered entries
selectedEntryId: null  // ID of currently selected entry
```

### Required Methods

#### 1. `init()`

**Purpose:** Initialize application, load data, setup event listeners, apply initial filters.

**Parameters:** None

**Return Type:** `Promise<void>` - Async initialization

**Implementation Steps:**

1. Try:
   - Call loadData() and await
   - Call setupEventListeners()
   - Call applyFilters()
2. Catch errors:
   - If error.message === 'file:// protocol detected':
     - Call showProtocolError()
   - Otherwise:
     - Log error to console
     - Display error message in content-list container

**Implementation Template:**

```javascript
async init() {
    try {
        await this.loadData();
        this.setupEventListeners();
        this.applyFilters();
    } catch (error) {
        if (error.message === 'file:// protocol detected') {
            this.showProtocolError();
        } else {
            console.error('Failed to initialize app:', error);
            document.getElementById('content-list').innerHTML =
                '<div class="no-content">Error loading content data</div>';
        }
    }
}
```

#### 2. `showProtocolError()`

**Purpose:** Display error message when file:// protocol detected.

**Return Type:** `undefined` - Directly modifies DOM

**DOM Manipulation:**

1. Hide header element: `document.querySelector('header').style.display = 'none'`
2. Hide filters section: `document.getElementById('filters').style.display = 'none'`
3. Get content container
4. Replace innerHTML with error message HTML

**Error Message HTML Structure:**

```html
<div class="protocol-error">
    <h2>⚠️ Local Server Required</h2>
    <p>This app must be run via a local HTTP server.</p>
    <p><strong>file:// is not supported</strong> due to browser security rules.</p>
    <h3>How to run:</h3>
    <ol>
        <li>Open a terminal in this directory</li>
        <li>Run: <code>python3 -m http.server</code></li>
        <li>Open: <code>http://localhost:8000</code></li>
    </ol>
</div>
```

**Implementation Template:**

```javascript
showProtocolError() {
    document.querySelector('header').style.display = 'none';
    document.getElementById('filters').style.display = 'none';

    const container = document.getElementById('content');
    container.innerHTML = `
        <div class="protocol-error">
            <h2>⚠️ Local Server Required</h2>
            <p>This app must be run via a local HTTP server.</p>
            <p><strong>file:// is not supported</strong> due to browser security rules.</p>
            <h3>How to run:</h3>
            <ol>
                <li>Open a terminal in this directory</li>
                <li>Run: <code>python3 -m http.server</code></li>
                <li>Open: <code>http://localhost:8000</code></li>
            </ol>
        </div>
    `;
}
```

#### 3. `loadData()`

**Purpose:** Load CSV and optional JSON data, normalize, link media, extract filter options.

**Parameters:** None

**Return Type:** `Promise<void>` - Async data loading

**Implementation Steps:**

1. Call DataIngestion.loadCSVFiles() and await
2. Store result in App.entries after normalization: `this.entries = DataNormalization.normalizeRows(rawRows)`
3. Call DataIngestion.loadMediaJSON() and await
4. Call DataNormalization.attachMedia(this.entries, mediaRecords)
5. Set App.filteredEntries to copy of entries: `this.filteredEntries = [...this.entries]`
6. Call DataNormalization.extractFilterOptions(this.entries)
7. Store result in filterOptions variable
8. Call Renderer.renderFilterUI(filterOptions, () => this.applyFilters())

**Implementation Template:**

```javascript
async loadData() {
    const rawRows = await DataIngestion.loadCSVFiles();
    this.entries = DataNormalization.normalizeRows(rawRows);

    const mediaRecords = await DataIngestion.loadMediaJSON();
    DataNormalization.attachMedia(this.entries, mediaRecords);

    this.filteredEntries = [...this.entries];

    const filterOptions = DataNormalization.extractFilterOptions(this.entries);
    Renderer.renderFilterUI(filterOptions, () => this.applyFilters());
}
```

#### 4. `setupEventListeners()`

**Purpose:** Set up all event listeners for application interactions.

**Parameters:** None

**Return Type:** `undefined` - Registers event handlers

**Event Listeners Required:**

1. Close Details Button:
   - Selector: `#close-details`
   - Event: 'click'
   - Handler: Set selectedEntryId to null, call hideDetailsPanel(), call highlightSelectedEntry(null)

**Implementation Template:**

```javascript
setupEventListeners() {
    document.getElementById('close-details').addEventListener('click', () => {
        this.selectedEntryId = null;
        Renderer.hideDetailsPanel();
        Renderer.highlightSelectedEntry(null);
    });
}
```

#### 5. `applyFilters()`

**Purpose:** Filter entries based on active filter selections and sort results.

**Parameters:** None

**Return Type:** `undefined` - Updates state and renders

**Implementation Steps:**

1. Call getActiveFilters() to get current filter values
2. Filter entries:
   - Filter this.entries array
   - For each entry, check if all active filters match
   - Filter logic: For each key in filters:
     - Get filterValue
     - If filterValue is falsy/empty, skip (no filter)
     - Get entryValue: entry[key]
     - Return entryValue === filterValue
3. Store filtered results in this.filteredEntries
4. Call sortEntries() to sort filteredEntries
5. Call Renderer.renderContentList(this.filteredEntries, (entry) => this.selectEntry(entry))

**Implementation Template:**

```javascript
applyFilters() {
    const filters = this.getActiveFilters();

    this.filteredEntries = this.entries.filter(entry => {
        return Object.keys(filters).every(key => {
            const filterValue = filters[key];
            if (!filterValue) return true;

            const entryValue = entry[key];
            return entryValue === filterValue;
        });
    });

    this.sortEntries();
    Renderer.renderContentList(this.filteredEntries, (entry) => this.selectEntry(entry));
}
```

#### 6. `getActiveFilters()`

**Purpose:** Get currently selected values from all filter dropdowns.

**Parameters:** None

**Return Type:** `Object` - Object with filter keys and selected values

**Implementation Steps:**

1. Create empty filters object
2. Select all elements: `#filter-container select`
3. For each select element:
   - Get ID: select.id
   - Extract key: remove 'filter-' prefix
   - Get value: select.value
   - Store in filters object: filters[key] = select.value
4. Return filters object

**Implementation Template:**

```javascript
getActiveFilters() {
    const filters = {};
    document.querySelectorAll('#filter-container select').forEach(select => {
        const key = select.id.replace('filter-', '');
        filters[key] = select.value;
    });
    return filters;
}
```

#### 7. `sortEntries()`

**Purpose:** Sort filteredEntries array based on defined sorting criteria.

**Parameters:** None

**Return Type:** `undefined` - Sorts filteredEntries in place

**Implementation Requirements:**

You MUST define sorting criteria specific to your data. Example (date-based):

```javascript
sortEntries() {
    this.filteredEntries.sort((a, b) => {
        if (a.releaseDate && b.releaseDate) {
            return new Date(a.releaseDate) - new Date(b.releaseDate);
        }
        if (a.releaseDate) return -1;
        if (b.releaseDate) return 1;
        return 0;
    });
}
```

**Sorting Rules:**
- Modify filteredEntries array in place using array.sort()
- Return negative number if a comes before b
- Return positive number if b comes before a
- Return 0 if equal
- Handle missing/null values appropriately

#### 8. `selectEntry(entry)`

**Purpose:** Handle selection of entry (row click), update state, render details, highlight row.

**Parameters:**
- `entry` (Object) - Selected entry object

**Return Type:** `undefined` - Updates state and renders

**Implementation Steps:**

1. Set this.selectedEntryId to entry.contentId
2. Call Renderer.renderDetailsPanel(entry)
3. Call Renderer.highlightSelectedEntry(entry.contentId)

**Implementation Template:**

```javascript
selectEntry(entry) {
    this.selectedEntryId = entry.contentId;
    Renderer.renderDetailsPanel(entry);
    Renderer.highlightSelectedEntry(entry.contentId);
}
```

---

## HTML Structure Requirements

### Required DOM Elements

#### Root Container

```html
<div id="app">
    <!-- All application content here -->
</div>
```

**Requirements:**
- Must have ID `app`
- Contains header, main sections

#### Header

```html
<header>
    <h1>Application Title</h1>
</header>
```

**Requirements:**
- Must contain application title
- Optional: Can include subtitle, navigation, etc.

#### Main Container

```html
<main>
    <section id="filters">
        <h2>Filters</h2>
        <div id="filter-container"></div>
    </section>

    <section id="content">
        <div id="content-list"></div>
    </section>

    <aside id="details-panel" class="hidden">
        <div class="close-btn" id="close-details">×</div>
        <h2 id="details-title"></h2>
        <div id="details-content"></div>
        <div id="attached-content">
            <h3>Attached Content</h3>
            <div id="attached-content-items"></div>
        </div>
    </aside>
</main>
```

**Required IDs:**
- `filters` - Filter sidebar section
- `filter-container` - Container for filter dropdowns
- `content` - Table content section
- `content-list` - Container for table or no-content message
- `details-panel` - Detail panel sidebar
- `close-details` - Close button for detail panel
- `details-title` - Title element in detail panel
- `details-content` - Container for detail items
- `attached-content` - Section for media attachments
- `attached-content-items` - Container for media elements

**Required Classes:**
- `hidden` - Applied to detail panel when not visible

### Script Loading Order

```html
<!-- Load in this exact order -->
<script src="js/data-ingestion.js"></script>
<script src="js/data-normalization.js"></script>
<script src="js/renderer.js"></script>
<script src="js/app.js"></script>

<!-- Initialize application -->
<script>
    document.addEventListener('DOMContentLoaded', () => App.init());
</script>
```

**Requirements:**
- DataIngestion module must load first
- DataNormalization depends on DataIngestion
- Renderer depends on DataNormalization
- App depends on all other modules
- Initialization must wait for DOMContentLoaded

---

## CSS Architecture Requirements

### CSS Variables (Required)

Define in `:root` selector:

```css
:root {
    /* Background Colors */
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-tertiary: #0f3460;

    /* Accent Colors */
    --accent-purple: #7b2cbf;
    --accent-pink: #c9184a;
    --accent-orange: #f77f00;
    --accent-teal: #00b4d8;

    /* Text Colors */
    --text-primary: #e8e8e8;
    --text-secondary: #b8b8b8;

    /* Border Colors */
    --border-color: #4a4e69;
}
```

**Requirements:**
- Must use CSS custom properties for theming
- Hex values shown are examples, customize as needed
- Variable names must match module expectations

### Global Reset

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

### Body Styles

```css
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    color: var(--text-primary);
    min-height: 100vh;
}
```

### App Container

```css
#app {
    display: flex;
    flex-direction: column;
    height: 100vh;
}
```

### Header Styles

```css
header {
    background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
    padding: 1.5rem 2rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

header h1 {
    font-size: 2rem;
    font-weight: 300;
    letter-spacing: 2px;
}
```

### Main Container Layout

```css
main {
    display: flex;
    flex: 1;
    overflow: hidden;
}
```

**Requirements:**
- Flexbox layout
- `overflow: hidden` to prevent body scroll

### Filters Sidebar

```css
#filters {
    width: 280px;
    background: var(--bg-tertiary);
    padding: 1.5rem;
    overflow-y: auto;
    border-right: 2px solid var(--border-color);
}

#filters h2 {
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    color: var(--accent-teal);
    text-transform: uppercase;
    letter-spacing: 1px;
}
```

### Filter Group Styles

```css
.filter-group {
    margin-bottom: 1.5rem;
}

.filter-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.filter-group select {
    width: 100%;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    border-radius: 5px;
    font-size: 0.95rem;
    cursor: pointer;
}

.filter-group select:focus {
    outline: none;
    border-color: var(--accent-teal);
}
```

### Content Section

```css
#content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
}

#content-list {
    overflow: auto;
}
```

### Table Styles

```css
.content-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.content-table thead {
    position: sticky;
    top: 0;
    background: linear-gradient(90deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    z-index: 10;
}

.content-table th {
    padding: 1rem 1.5rem;
    text-align: left;
    font-weight: 600;
    color: var(--accent-teal);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.8rem;
    border-bottom: 2px solid var(--accent-purple);
    white-space: nowrap;
}

.content-table td {
    padding: 0.75rem 1.5rem;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-color);
}
```

**Critical Requirements:**
- `position: sticky` on thead is REQUIRED for sticky headers
- `z-index: 10` ensures headers stay on top of scrolling content
- `white-space: nowrap` prevents header text wrapping

### Table Row Styles

```css
.table-row {
    cursor: pointer;
    transition: background 0.2s ease;
    background: var(--bg-secondary);
}

.table-row:hover {
    background: linear-gradient(90deg, rgba(15, 52, 96, 0.6) 0%, var(--bg-secondary) 100%);
}

.table-row.selected {
    background: linear-gradient(90deg, var(--accent-purple) 0%, var(--bg-tertiary) 100%);
    border-left: 4px solid var(--accent-orange);
}

.table-row.selected td {
    color: white;
    font-weight: 500;
}

.table-row.selected td[style*="background-color"] {
    background: rgba(123, 44, 191, 0.25) !important;
}
```

**Critical Requirements:**
- `cursor: pointer` indicates interactivity
- `transition` enables smooth hover effects
- `.selected` class added by JavaScript
- Last rule handles colored cells in selected rows

### Details Panel Styles

```css
#details-panel {
    width: 400px;
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
    border-left: 2px solid var(--border-color);
    padding: 2rem;
    overflow-y: auto;
    position: relative;
}

#details-panel.hidden {
    display: none;
}
```

**Critical Requirements:**
- `.hidden` class toggles visibility
- `position: relative` for close button positioning
- `overflow-y: auto` for scrolling content

### Close Button

```css
.close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 35px;
    height: 35px;
    background: var(--accent-pink);
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 1.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.close-btn:hover {
    background: var(--accent-orange);
    transform: rotate(90deg);
}
```

### Detail Item Styles

```css
.detail-item {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 8px;
    border-left: 4px solid var(--accent-purple);
}

.detail-label {
    font-size: 0.85rem;
    color: var(--accent-pink);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.detail-value {
    font-size: 1.1rem;
    color: var(--text-primary);
}
```

### Attached Content Section

```css
#attached-content {
    margin-top: 2.5rem;
    padding-top: 2rem;
    border-top: 2px solid var(--border-color);
}

#attached-content h3 {
    font-size: 1.2rem;
    color: var(--accent-orange);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

#attached-content-items {
    color: var(--text-secondary);
    font-style: italic;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 8px;
    border-left: 4px solid var(--accent-orange);
}
```

### Media Element Styles

```css
.media-wrapper {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 8px;
    border-left: 4px solid var(--accent-teal);
}

.media-type-label {
    font-size: 0.75rem;
    color: var(--accent-pink);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.media-wrapper video,
.media-wrapper audio,
.media-wrapper img {
    background: var(--bg-secondary);
    border-radius: 6px;
}
```

### Media Link Styles

```css
.media-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--bg-tertiary);
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
    border: 1px solid var(--border-color);
}

.media-link:hover {
    background: var(--accent-purple);
    transform: translateX(5px);
}

.media-link-icon {
    font-size: 1.5rem;
}

.media-link-text {
    color: var(--text-primary);
    font-weight: 500;
}
```

### Utility Styles

```css
.no-content {
    color: var(--text-secondary);
    font-style: italic;
}
```

### Scrollbar Styling

```css
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-purple);
}
```

### Protocol Error Styles

```css
.protocol-error {
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
    border-radius: 15px;
    padding: 3rem;
    max-width: 600px;
    margin: 2rem auto;
    text-align: center;
    border: 3px solid var(--accent-pink);
}

.protocol-error h2 {
    color: var(--accent-pink);
    font-size: 2rem;
    margin-bottom: 1.5rem;
}

.protocol-error h3 {
    color: var(--accent-teal);
    margin: 2rem 0 1rem 0;
    text-align: left;
}

.protocol-error p {
    font-size: 1.1rem;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.protocol-error ol {
    text-align: left;
    margin-left: 2rem;
    color: var(--text-secondary);
    line-height: 1.8;
}

.protocol-error code {
    background: var(--bg-primary);
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    color: var(--accent-orange);
    font-family: 'Courier New', monospace;
}
```

---

## Protocol and Server Requirements

### HTTP Server Requirement

**Mandatory:** This system MUST run on an HTTP server, not via file:// protocol.

**Reason:** Browser security blocks fetch() API on file:// protocol for local file access.

**Server Options:**

**Python 3:**
```bash
python3 -m http.server 8000
# Access at http://localhost:8000
```

**Node.js (http-server):**
```bash
npx http-server -p 8000
# Access at http://localhost:8000
```

**PHP:**
```bash
php -S localhost:8000
# Access at http://localhost:8000
```

**VS Code Live Server Extension:**
- Install "Live Server" extension
- Right-click index.html
- Select "Open with Live Server"
- Automatically opens on HTTP server

### Protocol Validation

The DataIngestion module includes `checkProtocol()` method that throws error on file://.

**Error Handling Flow:**
1. DataIngestion.checkProtocol() throws error
2. App.init() catches error
3. App.showProtocolError() displays user-friendly message
4. User sees instructions to start HTTP server

### Browser Compatibility

**Required Browser Features:**
- ES6 JavaScript support (arrow functions, template literals, async/await, spread operator)
- CSS Variables support
- Flexbox support
- Fetch API support
- Position: sticky support
- ClassList methods support

**Browser Support Matrix:**
- Chrome 49+ (2016)
- Firefox 44+ (2016)
- Safari 10.1+ (2017)
- Edge 79+ (2020)

---

## Data Flow Diagram

```
User opens dashboard.html
        ↓
DOMContentLoaded event fires
        ↓
App.init() called
        ↓
App.loadData()
        ├→ DataIngestion.loadCSVFiles()
        │   └→ fetch('data/content.csv')
        │       └→ DataIngestion.parseCSV()
        │           └→ Returns Array<Object>
        │
        ├→ DataNormalization.normalizeRows()
        │   └→ Map raw rows to normalized objects
        │
        ├→ DataIngestion.loadMediaJSON()
        │   └→ fetch('data/media.json')
        │       └→ Returns Array<Object> or []
        │
        ├→ DataNormalization.attachMedia()
        │   └→ Link media records to entries by contentId
        │
        ├→ App.entries = normalized entries
        ├→ App.filteredEntries = copy of entries
        │
        ├→ DataNormalization.extractFilterOptions()
        │   └→ Extract unique values for each field
        │       └→ Returns Object with filter options
        │
        └→ Renderer.renderFilterUI()
            └→ Generate dropdown elements
                └→ Append to #filter-container

        ↓
App.applyFilters()
        ├→ App.getActiveFilters()
        │   └→ Read values from all select elements
        │       └→ Returns Object with active filters
        │
        ├→ Filter App.entries based on active filters
        │   └→ Store result in App.filteredEntries
        │
        ├→ App.sortEntries()
        │   └→ Sort App.filteredEntries in place
        │
        └→ Renderer.renderContentList()
            ├→ Create table element
            ├→ Create thead with headers
            ├→ For each entry in App.filteredEntries:
            │   └→ Renderer.createTableRow()
            │       ├→ Create tr with class 'table-row'
            │       ├→ Set dataset.id to entry.contentId
            │       ├→ Create td cells for each column
            │       └→ Add click listener calling App.selectEntry(entry)
            └→ Append table to #content-list

        ↓
User clicks table row
        ↓
App.selectEntry(entry)
        ├→ App.selectedEntryId = entry.contentId
        ├→ Renderer.renderDetailsPanel(entry)
        │   ├→ Set #details-title text
        │   ├→ Clear #details-content
        │   ├→ Create detail-item divs for each field
        │   ├→ Renderer.renderAttachedMedia()
        │   │   └→ Create media elements from entry.attachedMedia
        │   └→ Remove 'hidden' class from #details-panel
        │
        └→ Renderer.highlightSelectedEntry(entry.contentId)
            ├→ Remove 'selected' class from all .table-row
            ├→ Find element with matching data-id
            ├→ Add 'selected' class
            └→ Scroll element into view

        ↓
User clicks close button
        ↓
Close button event handler
        ├→ App.selectedEntryId = null
        ├→ Renderer.hideDetailsPanel()
        │   └→ Add 'hidden' class to #details-panel
        └→ Renderer.highlightSelectedEntry(null)
            └→ Remove 'selected' class from all rows

        ↓
User changes filter dropdown
        ↓
Filter change event listener
        └→ App.applyFilters()
            └→ (Filter and re-render as shown above)
```

---

## Implementation Checklist

When implementing this visual database system, ensure:

### Data Layer
- [ ] CSV file has header row with unique identifier column
- [ ] CSV values properly quoted if containing commas
- [ ] Optional JSON file follows schema with content_id field
- [ ] Data directory structure matches file paths

### JavaScript Modules
- [ ] DataIngestion module loads first
- [ ] All async functions properly awaited
- [ ] CSV parsing handles quoted fields
- [ ] Date normalization handles invalid dates
- [ ] Protocol validation throws specific error message
- [ ] Data normalization maps all required fields
- [ ] Media attachment links by correct identifier field
- [ ] Filter options extracted from all fields except internal ones
- [ ] Renderer uses correct container IDs
- [ ] Table columns match your data structure
- [ ] Detail panel displays relevant fields
- [ ] Media elements handle both local and remote sources
- [ ] App state properly initialized
- [ ] Event listeners registered during init
- [ ] Sorting function defined for your data

### HTML Structure
- [ ] All required IDs present in DOM
- [ ] Scripts loaded in correct order
- [ ] Details panel has 'hidden' class initially
- [ ] Close button has correct ID

### CSS
- [ ] CSS variables defined in :root
- [ ] Flexbox layout properly configured
- [ ] Table header has position: sticky
- [ ] z-index set on sticky header
- [ ] .selected class defined for table rows
- [ ] .hidden class sets display: none
- [ ] Scrollbar styling included
- [ ] Transition effects defined

### Browser Environment
- [ ] Application running on HTTP server (not file://)
- [ ] Browser supports ES6 features
- [ ] Fetch API available
- [ ] No CORS errors (local server handles same-origin)

### Functionality
- [ ] Data loads successfully
- [ ] Table renders with all entries
- [ ] Filters work and update table
- [ ] Sorting works correctly
- [ ] Row click shows details panel
- [ ] Selected row highlighted
- [ ] Detail panel shows entry data
- [ ] Media attachments render correctly
- [ ] Close button hides details panel
- [ ] Error message displays on file:// protocol

---

## Customization Guide

### Adapting to Different Data Structures

**Step 1: Identify Your CSV Columns**

Review your CSV file and note:
- Unique identifier column (required)
- Date columns (for normalization)
- Text/categorical columns (for display and filtering)
- Optional related data fields

**Step 2: Update DataNormalization.normalizeRow()**

Map your CSV columns to normalized properties:

```javascript
normalizeRow(rawRow) {
    return {
        // REQUIRED: Unique identifier
        id: rawRow['id_column'] || '',

        // Date fields (normalize with normalizeDate)
        createdAt: this.normalizeDate(rawRow['Created Date'] || ''),
        updatedAt: this.normalizeDate(rawRow['Updated Date'] || ''),

        // Text/categorical fields
        name: rawRow['Name'] || '',
        category: rawRow['Category'] || '',
        status: rawRow['Status'] || '',

        // Path to related media (e.g., screenshot path)
        mediaPath: rawRow['Screenshot Path'] || '',

        // Related media array
        relatedMedia: []
    };
}
```

**Step 3: Define Table Columns**

In Renderer.renderContentList(), specify which fields to display:

```javascript
const headers = ['Name', 'Category', 'Status', 'Created Date'];
```

**Step 4: Update Table Row Creation**

In Renderer.createTableRow(), create cells for your data:

```javascript
createTableRow(entry, onSelectEntry) {
    const tr = document.createElement('tr');
    tr.className = 'table-row';
    tr.dataset.id = entry.id;

    tr.appendChild(this.createTableCell(entry.name || '-'));

    const categoryCell = this.createTableCell(entry.category || 'Uncategorized');
    if (entry.category) {
        const categoryColor = this.getCategoryColor(entry.category);
        categoryCell.style.backgroundColor = categoryColor;
    }
    tr.appendChild(categoryCell);

    tr.appendChild(this.createTableCell(entry.status || '-'));

    const dateCell = this.createTableCell(entry.createdAt || '-');
    tr.appendChild(dateCell);

    tr.addEventListener('click', () => onSelectEntry(entry));
    return tr;
}
```

**Step 5: Update Detail Panel Fields**

In Renderer.renderDetailsPanel(), specify which fields to show:

```javascript
const fields = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'category', label: 'Category' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Created Date' },
    { key: 'updatedAt', label: 'Updated Date' }
];
```

**Step 6: Implement Color Coding (Optional)**

Create color generation functions for your data:

```javascript
getCategoryColor(categoryName) {
    const colors = [
        'rgba(173, 216, 230, 0.12)',
        'rgba(255, 182, 193, 0.12)',
        // ... more colors
    ];

    let hash = 0;
    for (let i = 0; i < categoryName.length; i++) {
        hash = ((hash << 5) - hash) + categoryName.charCodeAt(i);
    }
    const index = Math.abs(hash) % colors.length;
    return colors[index];
}
```

**Step 7: Update Sorting**

In App.sortEntries(), define sorting for your data:

```javascript
sortEntries() {
    this.filteredEntries.sort((a, b) => {
        // Sort by creation date
        if (a.createdAt && b.createdAt) {
            return new Date(a.createdAt) - new Date(b.createdAt);
        }
        // Fall back to name
        if (a.name && b.name) {
            return a.name.localeCompare(b.name);
        }
        return 0;
    });
}
```

**Step 8: Customize CSS Theme**

Update CSS variables in :root:

```css
:root {
    --bg-primary: #your-color;
    --bg-secondary: #your-color;
    --bg-tertiary: #your-color;
    --accent-purple: #your-color;
    /* ... etc */
}
```

### Modifying Layout

**Change Panel Widths:**

```css
#filters {
    width: 320px;  /* Increase from 280px */
}

#details-panel {
    width: 500px;  /* Increase from 400px */
}
```

**Two-Panel Layout (No Filters):**

If you don't need filters, remove filters section:

```css
main {
    display: flex;
    flex: 1;
}

/* Remove filters section from HTML */

#content {
    flex: 1;
    /* Remove left padding */
}
```

**Full-Width Details Panel:**

To make details panel overlap content instead of pushing:

```css
#details-panel {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 20;
}
```

### Adding Image Preview

**If your CSV has image paths:**

1. Add mediaPath field to normalizeRow()
2. In renderDetailsPanel(), add image preview:

```javascript
renderDetailsPanel(entry) {
    // ... existing code ...

    if (entry.mediaPath) {
        const imageDiv = document.createElement('div');
        imageDiv.className = 'media-wrapper';

        const img = document.createElement('img');
        img.src = this.resolveImagePath(entry.mediaPath);
        img.style.width = '100%';
        img.style.maxHeight = '400px';
        img.style.objectFit = 'contain';
        img.style.borderRadius = '8px';

        imageDiv.appendChild(img);
        content.appendChild(imageDiv);
    }

    // ... rest of code ...
}
```

3. Add path resolution helper:

```javascript
resolveImagePath(path) {
    // Convert absolute path to relative if needed
    if (path.startsWith('/')) {
        return path.replace(/^\/.*?\//, '');
    }
    return path;
}
```

---

## Error Handling Best Practices

### Data Loading Errors

**CSV Not Found:**
```javascript
if (response.status === 404) {
    throw new Error('CSV file not found. Check data/content.csv exists.');
}
```

**Invalid CSV Format:**
```javascript
if (headers.length !== values.length) {
    console.warn('Skipping malformed row:', line);
    continue;
}
```

### Media Loading Errors

**Image Load Error:**
```javascript
img.onerror = function() {
    this.style.display = 'none';
    console.error('Failed to load image:', this.src);
};
```

**Video Load Error:**
```javascript
video.onerror = function() {
    console.error('Failed to load video:', this.src);
    this.style.display = 'none';
    const errorMsg = document.createElement('div');
    errorMsg.textContent = 'Video failed to load';
    errorMsg.style.color = 'var(--text-secondary)';
    this.parentNode.appendChild(errorMsg);
};
```

### Filter Errors

**Empty Results:**
```javascript
if (filteredEntries.length === 0) {
    container.innerHTML = '<div class="no-content">No entries match current filters</div>';
    return;
}
```

---

## Performance Considerations

### Large Datasets

**Implement Pagination (Optional):**

```javascript
const PAGE_SIZE = 50;
let currentPage = 1;

function renderPaginated() {
    const start = (currentPage - 1) * PAGE_SIZE;
    const end = start + PAGE_SIZE;
    const pageEntries = filteredEntries.slice(start, end);
    Renderer.renderContentList(pageEntries, onSelectEntry);
}
```

**Lazy Loading Images:**

```javascript
img.loading = 'lazy';
img.src = imagePath;
```

### Rendering Optimization

**Debounce Filter Changes:**

```javascript
let debounceTimer;
select.addEventListener('change', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => onFilterChange(), 300);
});
```

**DocumentFragment for Batch DOM Updates:**

```javascript
const fragment = document.createDocumentFragment();
entries.forEach(entry => {
    const row = createTableRow(entry, onSelectEntry);
    fragment.appendChild(row);
});
tbody.appendChild(fragment);
```

---

## Testing Guidelines

### Manual Testing Checklist

1. **Data Loading:**
   - Open dashboard.html on HTTP server
   - Verify table renders with all entries
   - Check no console errors

2. **Filtering:**
   - Change each filter dropdown
   - Verify table updates correctly
   - Check "All" option resets filter

3. **Sorting:**
   - Add entries with different values
   - Verify sort order is correct

4. **Row Selection:**
   - Click various rows
   - Verify details panel shows correct data
   - Check row is highlighted
   - Verify scroll-to-selection works

5. **Detail Panel:**
   - Verify all fields display
   - Check media elements load
   - Test close button functionality

6. **Error Handling:**
   - Try opening via file://
   - Verify protocol error message displays
   - Remove CSV file and verify error message
   - Add malformed CSV line and verify handling

### Browser Testing

Test in at least:
- Chrome
- Firefox
- Safari (if on macOS)

---

## Summary

This specification provides complete requirements for implementing a zero-dependency visual database system with:

- Dynamic CSV data loading
- Optional JSON attachments
- Filter UI generation
- Sortable table with sticky headers
- Detail panel with media support
- Color-coded cells
- Selection highlighting
- Protocol validation
- Zero external dependencies

Follow the implementation checklist, customize data mappings for your CSV structure, and ensure HTTP server hosting for proper functionality.
