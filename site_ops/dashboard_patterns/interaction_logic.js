/*
    ========================================
    VISUAL DATABASE JAVASCRIPT MODULES
    ========================================

    This file contains all four JavaScript modules
    required for implementing visual database system.

    Copy to: js/ (split into 4 files)

    File 1: data-ingestion.js (DataIngestion module)
    File 2: data-normalization.js (DataNormalization module)
    File 3: renderer.js (Renderer module)
    File 4: app.js (App module)

    Load order in HTML:
    1. data-ingestion.js
    2. data-normalization.js
    3. renderer.js
    4. app.js

    ========================================
*/

/*
    ========================================
    MODULE 1: DATA INGESTION
    ========================================

    Purpose: Load and parse CSV/JSON data files

    File: js/data-ingestion.js

    Contains:
    - Protocol validation
    - CSV file loading
    - JSON file loading
    - CSV parsing

    REQUIRED METHODS:
    - checkProtocol()
    - loadCSVFiles(dataPath)
    - loadMediaJSON(dataPath)
    - parseCSV(csvText)
    - parseCSVLine(line)
*/

const DataIngestion = {
    /*
        ========================================
        METHOD: checkProtocol()
        ========================================

        Purpose: Validate HTTP protocol (reject file://)

        Parameters: None

        Returns: Throws error if file:// detected

        Usage: Call at start of all data loading methods

        Browser Security:
        - fetch() API blocked on file:// protocol
        - Must run on HTTP server
        - This method prevents silent failures
    */
    checkProtocol() {
        /*
            Check window.location.protocol
            If equals 'file:', throw specific error
        */
        if (window.location.protocol === 'file:') {
            throw new Error('file:// protocol detected');
        }
    },

    /*
        ========================================
        METHOD: loadCSVFiles(dataPath)
        ========================================

        Purpose: Load and parse CSV file containing primary data

        Parameters:
        - dataPath (string, optional): Relative path to data directory
          Default: 'data/'

        Returns: Promise<Array<Object>>
        - Array of parsed row objects
        - Each object maps column headers to values

        Error Handling:
        - 404: File not found - throws error
        - 5xx: Server error - throws error
        - Network error - throws error
        - Protocol error - throws 'file:// protocol detected'

        Usage:
        const rows = await DataIngestion.loadCSVFiles('data/');
    */
    async loadCSVFiles(dataPath = 'data/') {
        try {
            // Step 1: Validate protocol
            this.checkProtocol();

            // Step 2: Construct fetch URL
            // Pattern: dataPath + 'content.csv'
            const response = await fetch(`${dataPath}content.csv`);

            // Step 3: Check HTTP response status
            if (!response.ok) {
                throw new Error(`Failed to load content.csv: ${response.statusText}`);
            }

            // Step 4: Get response text
            const csvText = await response.text();

            // Step 5: Parse CSV text
            return this.parseCSV(csvText);

        } catch (error) {
            // Step 6: Log and rethrow error
            console.error('Error loading CSV file:', error);
            throw error;
        }
    },

    /*
        ========================================
        METHOD: loadMediaJSON(dataPath)
        ========================================

        Purpose: Load optional JSON file containing media attachments

        Parameters:
        - dataPath (string, optional): Relative path to data directory
          Default: 'data/'

        Returns: Promise<Array<Object>>
        - Array of media record objects
        - Empty array if file not found (404)

        Error Handling:
        - 404: Returns empty array (file is optional)
        - Other errors: Throws error with status

        Usage:
        const media = await DataIngestion.loadMediaJSON('data/');
    */
    async loadMediaJSON(dataPath = 'data/') {
        try {
            // Step 1: Validate protocol
            this.checkProtocol();

            // Step 2: Construct fetch URL
            const response = await fetch(`${dataPath}media.json`);

            // Step 3: Check response status
            if (!response.ok) {
                // Step 4: 404 is OK - file is optional
                if (response.status === 404) {
                    return [];
                }
                // Step 5: Other errors are problematic
                throw new Error(`Failed to load media.json: ${response.statusText}`);
            }

            // Step 6: Parse JSON response
            const data = await response.json();
            return data;

        } catch (error) {
            // Step 7: Handle 404 case from error message
            if (error.message && error.message.includes('404')) {
                return [];
            }

            // Step 8: Log and rethrow other errors
            console.error('Error loading media.json:', error);
            throw error;
        }
    },

    /*
        ========================================
        METHOD: parseCSV(csvText)
        ========================================

        Purpose: Parse CSV text string into array of row objects

        Parameters:
        - csvText (string): Raw CSV file content

        Returns: Array<Object>
        - Array of row objects
        - Each object maps column headers to values
        - Empty array if CSV has no data rows

        CSV Format Requirements:
        - Header row on line 1
        - Comma delimiter
        - Double quotes for fields containing commas
        - LF or CRLF line endings

        Usage:
        const rows = DataIngestion.parseCSV(csvText);
    */
    parseCSV(csvText) {
        // Step 1: Trim whitespace
        const lines = csvText.trim().split('\n');

        // Step 2: Check if CSV has data rows
        if (lines.length < 2) {
            return [];
        }

        // Step 3: Parse first line as headers
        const headers = lines[0].split(',').map(h => h.trim());
        const rows = [];

        // Step 4: Iterate through data rows (skip header)
        for (let i = 1; i < lines.length; i++) {
            // Step 5: Parse row using quote-aware parser
            const values = this.parseCSVLine(lines[i]);

            // Step 6: Validate row has correct number of values
            if (values.length === headers.length) {
                // Step 7: Create row object mapping headers to values
                const row = {};
                headers.forEach((header, index) => {
                    row[header] = values[index] ? values[index].trim() : '';
                });
                rows.push(row);
            }
            // Step 8: Skip malformed rows silently
        }

        // Step 9: Return parsed rows
        return rows;
    },

    /*
        ========================================
        METHOD: parseCSVLine(line)
        ========================================

        Purpose: Parse single CSV line into array of field values
        Handles quoted fields correctly

        Parameters:
        - line (string): Single line from CSV (without newline)

        Returns: Array<string>
        - Array of field values
        - Handles commas inside quotes
        - Handles escaped quotes ("") inside quotes

        Parsing Algorithm:
        1. Iterate through each character
        2. Track quote state (inQuotes boolean)
        3. On quote: toggle inQuotes
        4. On comma when not inQuotes: end current field
        5. Otherwise: add character to current field
        6. Add final field after loop

        Usage:
        const values = DataIngestion.parseCSVLine(line);
    */
    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;

        // Step 1: Iterate through each character
        for (let i = 0; i < line.length; i++) {
            const char = line[i];

            // Step 2: Check for quote
            if (char === '"') {
                // Step 3: Toggle quote state
                inQuotes = !inQuotes;
            }
            // Step 4: Check for comma outside quotes
            else if (char === ',' && !inQuotes) {
                // Step 5: End current field
                result.push(current);
                current = '';
            }
            // Step 6: Add character to current field
            else {
                current += char;
            }
        }

        // Step 7: Add final field
        result.push(current);

        // Step 8: Return array of values
        return result;
    }
};

/*
    ========================================
    MODULE 2: DATA NORMALIZATION
    ========================================

    Purpose: Transform raw CSV data into normalized objects

    File: js/data-normalization.js

    Contains:
    - Row normalization
    - Date normalization
    - Media attachment linking
    - Filter option extraction

    REQUIRED METHODS:
    - normalizeRows(rawRows)
    - normalizeRow(rawRow)
    - normalizeDate(dateString)
    - attachMedia(entries, mediaRecords)
    - extractFilterOptions(entries)

    CUSTOMIZATION:
    - normalizeRow() MUST be adapted to your CSV structure
    - Map your column names to property names
*/

const DataNormalization = {
    /*
        ========================================
        METHOD: normalizeRows(rawRows)
        ========================================

        Purpose: Transform array of raw CSV rows into normalized entries

        Parameters:
        - rawRows (Array<Object>): Array from CSV parser

        Returns: Array<Object>
        - Array of normalized entry objects

        Usage:
        const entries = DataNormalization.normalizeRows(rawRows);
    */
    normalizeRows(rawRows) {
        // Map each raw row to normalized entry
        return rawRows.map(row => this.normalizeRow(row));
    },

    /*
        ========================================
        METHOD: normalizeRow(rawRow)
        ========================================

        Purpose: Transform single raw CSV row into normalized entry

        Parameters:
        - rawRow (Object): Single raw row object

        Returns: Object
        - Normalized entry object

        CUSTOMIZATION REQUIRED:
        Adapt this method to your CSV structure!

        Example CSV:
        content_id,Name,Category,Status,Created Date
        ID-001,Item One,Category A,Active,2025-01-15

        Example Mapping:
        {
            id: rawRow['content_id'],
            name: rawRow['Name'],
            category: rawRow['Category'],
            status: rawRow['Status'],
            createdAt: normalizeDate(rawRow['Created Date'])
        }
    */
    normalizeRow(rawRow) {
        // CRITICAL: Adapt this mapping to your CSV structure!

        // Example mapping (adjust to your data):
        return {
            // REQUIRED: Unique identifier
            contentId: rawRow['content_id'] || '',

            // OPTIONAL: Date fields (normalize to ISO format)
            releaseDate: this.normalizeDate(rawRow['Release Date'] || ''),
            weekOf: this.normalizeDate(rawRow['Week of x'] || rawRow['Week Of'] || ''),

            // OPTIONAL: Categorical fields
            showType: rawRow['Show/Content Type'] || rawRow['Show or Content Type'] || '',
            season: rawRow['Season'] || '',
            episode: rawRow['Episode'] || '',
            month: rawRow['Month'] || '',

            // OPTIONAL: Text fields
            mediaSource: rawRow['Media Source'] || '',

            // REQUIRED: Array for media attachments (populated later)
            attachedMedia: []
        };
    },

    /*
        ========================================
        METHOD: normalizeDate(dateString)
        ========================================

        Purpose: Convert date string to ISO 8601 format

        Parameters:
        - dateString (string): Date string from CSV

        Returns: string
        - ISO format date (YYYY-MM-DD) if valid
        - Original string if invalid
        - Empty string if falsy

        Supported Input Formats:
        - ISO 8601: 2025-10-03
        - US Format: 10/3/2025 or 10/03/2025
        - With time: 2025-10-03T14:30:00Z
        - Any format JavaScript Date() can parse

        Usage:
        const isoDate = DataNormalization.normalizeDate('10/3/2025');
        // Returns: '2025-10-03'
    */
    normalizeDate(dateString) {
        // Step 1: Return empty string for falsy values
        if (!dateString) return '';

        // Step 2: Create Date object from string
        const date = new Date(dateString);

        // Step 3: Check if date is invalid
        if (isNaN(date.getTime())) {
            // Step 4: Return original string if invalid
            return dateString;
        }

        // Step 5: Convert to ISO format (YYYY-MM-DD)
        return date.toISOString().split('T')[0];
    },

    /*
        ========================================
        METHOD: attachMedia(entries, mediaRecords)
        ========================================

        Purpose: Link media records to entries by identifier

        Parameters:
        - entries (Array<Object>): Normalized entry objects
        - mediaRecords (Array<Object>): Media record objects from JSON

        Returns: undefined (modifies entries in place)

        Relationship:
        - One entry can have multiple media records
        - Linked by content_id field

        Usage:
        DataNormalization.attachMedia(entries, mediaRecords);
    */
    attachMedia(entries, mediaRecords) {
        // Step 1: Create lookup map
        const mediaMap = {};

        // Step 2: Build map of contentId -> media records
        mediaRecords.forEach(record => {
            const contentId = record.content_id;
            if (!mediaMap[contentId]) {
                mediaMap[contentId] = [];
            }
            mediaMap[contentId].push(record);
        });

        // Step 3: Attach media to matching entries
        entries.forEach(entry => {
            if (mediaMap[entry.contentId]) {
                entry.attachedMedia = mediaMap[entry.contentId];
            }
            // If no matching media, attachedMedia remains empty array
        });
    },

    /*
        ========================================
        METHOD: extractFilterOptions(entries)
        ========================================

        Purpose: Extract unique values for filter dropdowns

        Parameters:
        - entries (Array<Object>): Normalized entry objects

        Returns: Object
        - Keys: field names
        - Values: sorted arrays of unique values

        Example:
        {
            showType: ['Category A', 'Category B'],
            status: ['Active', 'Inactive', 'Pending']
        }

        Usage:
        const options = DataNormalization.extractFilterOptions(entries);
    */
    extractFilterOptions(entries) {
        const options = {};

        // Step 1: Iterate through each entry
        entries.forEach(entry => {
            // Step 2: Iterate through each field
            Object.keys(entry).forEach(key => {
                // Step 3: Skip internal fields
                if (key === 'contentId' || key === 'attachedMedia') return;

                // Step 4: Get field value
                const value = entry[key];

                // Step 5: Add value to options if truthy
                if (value && value !== '') {
                    if (!options[key]) {
                        options[key] = new Set();
                    }
                    options[key].add(value);
                }
            });
        });

        // Step 6: Convert Sets to sorted arrays
        Object.keys(options).forEach(key => {
            options[key] = Array.from(options[key]).sort();
        });

        // Step 7: Return filter options
        return options;
    }
};

/*
    ========================================
    MODULE 3: RENDERER
    ========================================

    Purpose: Generate all UI components dynamically

    File: js/renderer.js

    Contains:
    - Filter UI generation
    - Table rendering
    - Detail panel rendering
    - Media element creation

    REQUIRED METHODS:
    - renderFilterUI(filterOptions, onFilterChange)
    - formatFilterLabel(key)
    - renderContentList(entries, onSelectEntry)
    - createTableRow(entry, onSelectEntry)
    - createTableCell(text)
    - renderDetailsPanel(entry)
    - createDetailItem(label, value)
    - renderAttachedMedia(entry)
    - createMediaElement(media)
    - createLocalMedia(media)
    - createRemoteEmbed(media)
    - createRemoteLink(media)
    - hideDetailsPanel()
    - highlightSelectedEntry(entryId)

    CUSTOMIZATION:
    - define table columns in renderContentList()
    - define cell creation in createTableRow()
    - define detail fields in renderDetailsPanel()
    - optional: color generation functions
*/

const Renderer = {
    /*
        ========================================
        OPTIONAL CONFIGURATION ARRAYS
        ========================================

        These are example arrays for color coding.
        Remove or adapt as needed for your data.
    */

    // Month names array (1 = January)
    monthNames: [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ],

    // Month background colors (index 0 = January)
    monthColors: [
        'rgba(255, 182, 193, 0.15)',   // January - light pink
        'rgba(173, 216, 230, 0.15)',   // February - light blue
        'rgba(144, 238, 144, 0.15)',   // March - light green
        'rgba(255, 218, 185, 0.15)',   // April - peach
        'rgba(221, 160, 221, 0.15)',   // May - plum
        'rgba(255, 255, 153, 0.15)',   // June - light yellow
        'rgba(255, 160, 122, 0.15)',   // July - light salmon
        'rgba(250, 128, 114, 0.12)',   // August - salmon
        'rgba(216, 191, 216, 0.15)',   // September - thistle
        'rgba(255, 200, 150, 0.15)',   // October - light orange
        'rgba(176, 224, 230, 0.15)',   // November - powder blue
        'rgba(255, 228, 225, 0.15)'    // December - misty rose
    ],

    /*
        ========================================
        METHOD: getMonthName(monthValue)
        ========================================

        Purpose: Convert month number to name

        Parameters:
        - monthValue (string|number): Month number (1-12)

        Returns: string
        - Month name or original value if invalid

        Usage:
        const name = Renderer.getMonthName('3');
        // Returns: 'March'
    */
    getMonthName(monthValue) {
        const monthNum = parseInt(monthValue);
        // Validate month number
        if (isNaN(monthNum) || monthNum < 1 || monthNum > 12) {
            return monthValue || '-';
        }
        return this.monthNames[monthNum - 1];
    },

    /*
        ========================================
        METHOD: getMonthColor(monthValue)
        ========================================

        Purpose: Get background color for month cell

        Parameters:
        - monthValue (string|number): Month number (1-12)

        Returns: string
        - RGBA color or empty string if invalid

        Usage:
        const color = Renderer.getMonthColor('3');
        // Returns: 'rgba(144, 238, 144, 0.15)'
    */
    getMonthColor(monthValue) {
        const monthNum = parseInt(monthValue);
        // Validate month number
        if (isNaN(monthNum) || monthNum < 1 || monthNum > 12) {
            return '';
        }
        return this.monthColors[monthNum - 1];
    },

    /*
        ========================================
        OPTIONAL METHOD: getShowColor(showName)
        ========================================

        Purpose: Generate consistent color for show/category

        Parameters:
        - showName (string): Show or category name

        Returns: string
        - RGBA color based on hash of name

        Algorithm:
        - Hash string to number
        - Modulo hash by number of colors
        - Return color at that index

        Usage:
        const color = Renderer.getShowColor('My Show');
        // Returns: consistent color for 'My Show'
    */
    getShowColor(showName) {
        const colors = [
            'rgba(173, 216, 230, 0.12)',
            'rgba(255, 182, 193, 0.12)',
            'rgba(144, 238, 144, 0.12)',
            'rgba(255, 218, 185, 0.12)',
            'rgba(221, 160, 221, 0.12)',
            'rgba(255, 255, 153, 0.12)',
            'rgba(255, 160, 122, 0.12)',
            'rgba(230, 230, 250, 0.12)',
            'rgba(152, 251, 152, 0.12)',
            'rgba(255, 200, 150, 0.12)'
        ];

        let hash1 = 0, hash2 = 0;
        // Hash string to number
        for (let i = 0; i < showName.length; i++) {
            const char = showName.charCodeAt(i);
            hash1 = ((hash1 << 5) - hash1) + char;
            hash2 = ((hash2 << 3) - hash2) + char + i;
        }

        const combined = Math.abs(hash1 + hash2);
        const index = combined % colors.length;
        return colors[index];
    },

    /*
        ========================================
        METHOD: renderFilterUI(filterOptions, onFilterChange)
        ========================================

        Purpose: Generate filter dropdown interface

        Parameters:
        - filterOptions (Object): From extractFilterOptions()
        - onFilterChange (Function): Callback on filter change

        Returns: undefined (modifies DOM)

        Generated Structure:
        <div class="filter-group">
            <label>Field Name</label>
            <select id="filter-fieldName">
                <option value="">All</option>
                <option value="Value1">Value1</option>
            </select>
        </div>

        Usage:
        Renderer.renderFilterUI(options, () => App.applyFilters());
    */
    renderFilterUI(filterOptions, onFilterChange) {
        // Step 1: Get filter container
        const container = document.getElementById('filter-container');

        // Step 2: Clear existing filters
        container.innerHTML = '';

        // Step 3: Iterate through filter options
        Object.keys(filterOptions).forEach(key => {
            // Step 4: Create filter group container
            const group = document.createElement('div');
            group.className = 'filter-group';

            // Step 5: Create label element
            const label = document.createElement('label');
            label.textContent = this.formatFilterLabel(key);
            group.appendChild(label);

            // Step 6: Create select element
            const select = document.createElement('select');
            select.id = `filter-${key}`;

            // Step 7: Add "All" option
            const allOption = document.createElement('option');
            allOption.value = '';
            allOption.textContent = 'All';
            select.appendChild(allOption);

            // Step 8: Add value options
            filterOptions[key].forEach(value => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                select.appendChild(option);
            });

            // Step 9: Add change event listener
            select.addEventListener('change', () => onFilterChange());
            group.appendChild(select);

            // Step 10: Append filter group to container
            container.appendChild(group);
        });
    },

    /*
        ========================================
        METHOD: formatFilterLabel(key)
        ========================================

        Purpose: Convert camelCase to human-readable label

        Parameters:
        - key (string): Property name (e.g., 'releaseDate')

        Returns: string
        - Human-readable label (e.g., 'Release Date')

        Transformation:
        - Capitalize first letter
        - Insert space before uppercase letters

        Usage:
        const label = Renderer.formatFilterLabel('releaseDate');
        // Returns: 'Release Date'
    */
    formatFilterLabel(key) {
        return key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
    },

    /*
        ========================================
        METHOD: renderContentList(entries, onSelectEntry)
        ========================================

        Purpose: Render table of entries

        Parameters:
        - entries (Array<Object>): Entries to display
        - onSelectEntry (Function): Callback for row click

        Returns: undefined (modifies DOM)

        CUSTOMIZATION REQUIRED:
        Define your table columns here!

        Usage:
        Renderer.renderContentList(filteredEntries, (entry) => App.selectEntry(entry));
    */
    renderContentList(entries, onSelectEntry) {
        // Step 1: Get content list container
        const container = document.getElementById('content-list');

        // Step 2: Clear existing content
        container.innerHTML = '';

        // Step 3: Check if entries exist
        if (entries.length === 0) {
            container.innerHTML = '<div class="no-content">No content entries found</div>';
            return;
        }

        // Step 4: Create table element
        const table = document.createElement('table');
        table.className = 'content-table';

        // Step 5: Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');

        // CRITICAL: Define your table columns here
        const headers = ['Release Date', 'Show Type', 'Season', 'Episode', 'Month'];
        headers.forEach((header, index) => {
            const th = document.createElement('th');
            th.textContent = header;
            th.dataset.columnIndex = index; // For optional sorting
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Step 6: Create table body
        const tbody = document.createElement('tbody');
        entries.forEach(entry => {
            const row = this.createTableRow(entry, onSelectEntry);
            tbody.appendChild(row);
        });
        table.appendChild(tbody);

        // Step 7: Append table to container
        container.appendChild(table);
    },

    /*
        ========================================
        METHOD: createTableRow(entry, onSelectEntry)
        ========================================

        Purpose: Create single table row

        Parameters:
        - entry (Object): Entry object to render
        - onSelectEntry (Function): Click callback

        Returns: HTMLElement
        - tr element with td children

        CUSTOMIZATION REQUIRED:
        Define which fields go in which columns!

        Usage:
        const row = Renderer.createTableRow(entry, (entry) => App.selectEntry(entry));
    */
    createTableRow(entry, onSelectEntry) {
        // Step 1: Create row element
        const tr = document.createElement('tr');
        tr.className = 'table-row';
        tr.dataset.id = entry.contentId;

        // CRITICAL: Define cell creation here
        // Must match header order from renderContentList()

        // Column 1: Release Date
        tr.appendChild(this.createTableCell(entry.releaseDate || '-'));

        // Column 2: Show Type (with color coding)
        const showCell = this.createTableCell(entry.showType || 'Untitled');
        if (entry.showType) {
            const showColor = this.getShowColor(entry.showType);
            showCell.style.backgroundColor = showColor;
        }
        tr.appendChild(showCell);

        // Column 3: Season
        tr.appendChild(this.createTableCell(entry.season || '-'));

        // Column 4: Episode
        tr.appendChild(this.createTableCell(entry.episode || '-'));

        // Column 5: Month (with color coding)
        const monthCell = this.createTableCell(this.getMonthName(entry.month));
        const monthColor = this.getMonthColor(entry.month);
        if (monthColor) {
            monthCell.style.backgroundColor = monthColor;
        }
        tr.appendChild(monthCell);

        // Step 2: Add click event listener
        tr.addEventListener('click', () => onSelectEntry(entry));

        // Step 3: Return row
        return tr;
    },

    /*
        ========================================
        METHOD: createTableCell(text)
        ========================================

        Purpose: Create table cell with text

        Parameters:
        - text (string): Cell content

        Returns: HTMLElement
        - td element

        Usage:
        const cell = Renderer.createTableCell('Value');
    */
    createTableCell(text) {
        const td = document.createElement('td');
        td.textContent = text;
        return td;
    },

    /*
        ========================================
        METHOD: renderDetailsPanel(entry)
        ========================================

        Purpose: Render detail panel for selected entry

        Parameters:
        - entry (Object): Selected entry object

        Returns: undefined (modifies DOM)

        CUSTOMIZATION REQUIRED:
        Define which fields to display!

        Usage:
        Renderer.renderDetailsPanel(selectedEntry);
    */
    renderDetailsPanel(entry) {
        // Step 1: Get DOM elements
        const panel = document.getElementById('details-panel');
        const title = document.getElementById('details-title');
        const content = document.getElementById('details-content');

        // Step 2: Set panel title
        title.textContent = entry.showType || 'Untitled';

        // Step 3: Clear existing content
        content.innerHTML = '';

        // Step 4: Display unique identifier
        if (entry.contentId) {
            content.appendChild(this.createDetailItem('Content ID', entry.contentId));
        }

        // CRITICAL: Define fields to display here
        const fields = [
            { key: 'releaseDate', label: 'Release Date' },
            { key: 'weekOf', label: 'Week Of' },
            { key: 'month', label: 'Month' },
            { key: 'season', label: 'Season' },
            { key: 'episode', label: 'Episode' },
            { key: 'mediaSource', label: 'Media Source' }
        ];

        // Step 5: Create detail items for each field
        fields.forEach(field => {
            if (entry[field.key] && entry[field.key] !== '') {
                content.appendChild(this.createDetailItem(field.label, entry[field.key]));
            }
        });

        // Step 6: Render attached media
        this.renderAttachedMedia(entry);

        // Step 7: Show panel
        panel.classList.remove('hidden');
    },

    /*
        ========================================
        METHOD: createDetailItem(label, value)
        ========================================

        Purpose: Create detail item with label and value

        Parameters:
        - label (string): Field label
        - value (string): Field value

        Returns: HTMLElement
        - div with detail-item class

        Generated Structure:
        <div class="detail-item">
            <div class="detail-label">LABEL</div>
            <div class="detail-value">VALUE</div>
        </div>

        Usage:
        const item = Renderer.createDetailItem('Name', 'John Doe');
    */
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
    },

    /*
        ========================================
        METHOD: renderAttachedMedia(entry)
        ========================================

        Purpose: Render media attachments in detail panel

        Parameters:
        - entry (Object): Entry with attachedMedia array

        Returns: undefined (modifies DOM)

        Usage:
        Renderer.renderAttachedMedia(entry);
    */
    renderAttachedMedia(entry) {
        const container = document.getElementById('attached-content-items');

        // Check if media exists
        if (entry.attachedMedia && entry.attachedMedia.length > 0) {
            container.innerHTML = '';
            // Create media element for each attachment
            entry.attachedMedia.forEach(media => {
                const mediaEl = this.createMediaElement(media);
                container.appendChild(mediaEl);
            });
        } else {
            container.innerHTML = '<div class="no-content">No media attached yet.</div>';
        }
    },

    /*
        ========================================
        METHOD: createMediaElement(media)
        ========================================

        Purpose: Create media element wrapper

        Parameters:
        - media (Object): Media record with type, source, path/url

        Returns: HTMLElement
        - div wrapper containing media element or link

        Usage:
        const mediaEl = Renderer.createMediaElement(mediaRecord);
    */
    createMediaElement(media) {
        const wrapper = document.createElement('div');
        wrapper.className = 'media-wrapper';

        // Create type label
        const typeLabel = document.createElement('div');
        typeLabel.className = 'media-type-label';
        typeLabel.textContent = `${media.type.toUpperCase()} - ${media.source.toUpperCase()}`;
        wrapper.appendChild(typeLabel);

        // Handle based on source
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
    },

    /*
        ========================================
        METHOD: createLocalMedia(media)
        ========================================

        Purpose: Create HTML5 media element for local file

        Parameters:
        - media (Object): Media record with type and path

        Returns: HTMLElement
        - video, audio, or img element

        Usage:
        const element = Renderer.createLocalMedia(mediaRecord);
    */
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
    },

    /*
        ========================================
        METHOD: createRemoteEmbed(media)
        ========================================

        Purpose: Create embedded HTML5 media for remote URL

        Parameters:
        - media (Object): Media record with type and url

        Returns: HTMLElement | null
        - video or audio element, or null if not embeddable

        Usage:
        const element = Renderer.createRemoteEmbed(mediaRecord);
    */
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
    },

    /*
        ========================================
        METHOD: createRemoteLink(media)
        ========================================

        Purpose: Create link to remote media

        Parameters:
        - media (Object): Media record with type and url

        Returns: HTMLElement
        - anchor element

        Usage:
        const link = Renderer.createRemoteLink(mediaRecord);
    */
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
    },

    /*
        ========================================
        METHOD: hideDetailsPanel()
        ========================================

        Purpose: Hide detail panel

        Parameters: None

        Returns: undefined (modifies DOM)

        Usage:
        Renderer.hideDetailsPanel();
    */
    hideDetailsPanel() {
        const panel = document.getElementById('details-panel');
        panel.classList.add('hidden');
    },

    /*
        ========================================
        METHOD: highlightSelectedEntry(entryId)
        ========================================

        Purpose: Highlight selected row and scroll into view

        Parameters:
        - entryId (string | null): ID of selected entry

        Returns: undefined (modifies DOM)

        Usage:
        Renderer.highlightSelectedEntry('ID-001');
        Renderer.highlightSelectedEntry(null); // Clear selection
    */
    highlightSelectedEntry(entryId) {
        // Step 1: Remove selected class from all rows
        document.querySelectorAll('.table-row').forEach(el => {
            el.classList.remove('selected');
        });

        // Step 2: Highlight selected row if provided
        if (entryId) {
            const selected = document.querySelector(`[data-id="${entryId}"]`);
            if (selected) {
                selected.classList.add('selected');
                // Step 3: Scroll to selection
                selected.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }
};

/*
    ========================================
    MODULE 4: APPLICATION
    ========================================

    Purpose: Orchestrate entire application

    File: js/app.js

    Contains:
    - State management
    - Data loading coordination
    - Event handling
    - Filter application
    - Entry selection

    REQUIRED METHODS:
    - init()
    - showProtocolError()
    - loadData()
    - setupEventListeners()
    - applyFilters()
    - getActiveFilters()
    - sortEntries()
    - selectEntry(entry)

    CUSTOMIZATION:
    - sortEntries() for your sorting criteria
*/

const App = {
    /*
        ========================================
        STATE PROPERTIES
        ========================================

        entries (Array): All loaded entries
        filteredEntries (Array): Currently filtered entries
        selectedEntryId (string | null): ID of selected entry
    */
    entries: [],
    filteredEntries: [],
    selectedEntryId: null,

    /*
        ========================================
        METHOD: init()
        ========================================

        Purpose: Initialize application

        Parameters: None

        Returns: Promise<void>

        Usage:
        document.addEventListener('DOMContentLoaded', () => App.init());
    */
    async init() {
        try {
            // Step 1: Load data
            await this.loadData();

            // Step 2: Setup event listeners
            this.setupEventListeners();

            // Step 3: Apply initial filters
            this.applyFilters();

        } catch (error) {
            // Step 4: Handle protocol error
            if (error.message === 'file:// protocol detected') {
                this.showProtocolError();
            } else {
                // Step 5: Handle other errors
                console.error('Failed to initialize app:', error);
                document.getElementById('content-list').innerHTML =
                    '<div class="no-content">Error loading content data</div>';
            }
        }
    },

    /*
        ========================================
        METHOD: showProtocolError()
        ========================================

        Purpose: Display protocol error message

        Parameters: None

        Returns: undefined (modifies DOM)

        Usage:
        App.showProtocolError();
    */
    showProtocolError() {
        // Hide header and filters
        document.querySelector('header').style.display = 'none';
        document.getElementById('filters').style.display = 'none';

        // Display error message
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
    },

    /*
        ========================================
        METHOD: loadData()
        ========================================

        Purpose: Load all data and prepare application

        Parameters: None

        Returns: Promise<void>

        Usage:
        await App.loadData();
    */
    async loadData() {
        // Step 1: Load CSV file
        const rawRows = await DataIngestion.loadCSVFiles();
        this.entries = DataNormalization.normalizeRows(rawRows);

        // Step 2: Load JSON file (optional)
        const mediaRecords = await DataIngestion.loadMediaJSON();
        DataNormalization.attachMedia(this.entries, mediaRecords);

        // Step 3: Initialize filtered entries
        this.filteredEntries = [...this.entries];

        // Step 4: Extract filter options
        const filterOptions = DataNormalization.extractFilterOptions(this.entries);
        Renderer.renderFilterUI(filterOptions, () => this.applyFilters());
    },

    /*
        ========================================
        METHOD: setupEventListeners()
        ========================================

        Purpose: Set up all event listeners

        Parameters: None

        Returns: undefined (registers event handlers)

        Usage:
        App.setupEventListeners();
    */
    setupEventListeners() {
        // Close details button
        document.getElementById('close-details').addEventListener('click', () => {
            this.selectedEntryId = null;
            Renderer.hideDetailsPanel();
            Renderer.highlightSelectedEntry(null);
        });
    },

    /*
        ========================================
        METHOD: applyFilters()
        ========================================

        Purpose: Apply filters and sort entries

        Parameters: None

        Returns: undefined (updates state and renders)

        Usage:
        App.applyFilters();
    */
    applyFilters() {
        // Step 1: Get active filter values
        const filters = this.getActiveFilters();

        // Step 2: Filter entries
        this.filteredEntries = this.entries.filter(entry => {
            return Object.keys(filters).every(key => {
                const filterValue = filters[key];
                if (!filterValue) return true;

                const entryValue = entry[key];
                return entryValue === filterValue;
            });
        });

        // Step 3: Sort filtered entries
        this.sortEntries();

        // Step 4: Render table
        Renderer.renderContentList(this.filteredEntries, (entry) => this.selectEntry(entry));
    },

    /*
        ========================================
        METHOD: getActiveFilters()
        ========================================

        Purpose: Get current filter values

        Parameters: None

        Returns: Object
        - Keys: field names
        - Values: selected filter values (empty string if none)

        Usage:
        const filters = App.getActiveFilters();
    */
    getActiveFilters() {
        const filters = {};
        document.querySelectorAll('#filter-container select').forEach(select => {
            const key = select.id.replace('filter-', '');
            filters[key] = select.value;
        });
        return filters;
    },

    /*
        ========================================
        METHOD: sortEntries()
        ========================================

        Purpose: Sort filtered entries

        Parameters: None

        Returns: undefined (sorts filteredEntries in place)

        CUSTOMIZATION REQUIRED:
        Define sorting criteria for your data!

        Example: Sort by release date
        */
    sortEntries() {
        this.filteredEntries.sort((a, b) => {
            // Sort by release date
            if (a.releaseDate && b.releaseDate) {
                return new Date(a.releaseDate) - new Date(b.releaseDate);
            }
            if (a.releaseDate) return -1;
            if (b.releaseDate) return 1;
            return 0;
        });
    },

    /*
        ========================================
        METHOD: selectEntry(entry)
        ========================================

        Purpose: Handle entry selection

        Parameters:
        - entry (Object): Selected entry object

        Returns: undefined (updates state and renders)

        Usage:
        App.selectEntry(entry);
    */
    selectEntry(entry) {
        this.selectedEntryId = entry.contentId;
        Renderer.renderDetailsPanel(entry);
        Renderer.highlightSelectedEntry(entry.contentId);
    }
};

/*
    ========================================
    INITIALIZATION
    ========================================

    Wait for DOM to load before initializing.

    Place in HTML after all script tags:
    <script>
        document.addEventListener('DOMContentLoaded', () => App.init());
    </script>
*/

document.addEventListener('DOMContentLoaded', () => App.init());

/*
    ========================================
    END OF JAVASCRIPT MODULES
    ========================================

    Split this file into 4 separate files:

    1. js/data-ingestion.js
       - Contains DataIngestion module

    2. js/data-normalization.js
       - Contains DataNormalization module

    3. js/renderer.js
       - Contains Renderer module

    4. js/app.js
       - Contains App module
       - Includes initialization at bottom

    Load in this order in HTML:
    <script src="js/data-ingestion.js"></script>
    <script src="js/data-normalization.js"></script>
    <script src="js/renderer.js"></script>
    <script src="js/app.js"></script>

    ========================================
*/
