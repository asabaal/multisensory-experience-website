/**
 * Site Maintenance Database - Application Logic
 * 
 * Handles CSV parsing, filtering, table rendering, and details panel management
 */

class MaintenanceDatabase {
    constructor() {
        this.allRows = [];
        this.filteredRows = [];
        this.selectedRow = null;
        this.filters = {
            pageType: 'all',
            mobile: 'all',
            issues: 'all'
            search: ''
        };
    }

    // State management
    async init() {
        await this.loadCSV();
        this.renderTable();
        this.setupEventListeners();
        this.showLoadingState(false);
    }

    // Load CSV with PapaParse
    async loadCSV() {
        this.showLoadingState(true);
        
        try {
            const response = await fetch('../site_maintenance_log.csv');
            const csvText = await response.text();
            
            const data = Papa.parse(csvText, {
                header: true,
                dynamicTyping: true
                skipEmptyLines: true,
                complete: true
            });
            
            this.allRows = data.data.map((row, index) => {
                const pageType = this.determinePageType(row);
                return {
                    ...row,
                    _id: index,
                    pageType: pageType
                };
            });
            
            this.filteredRows = [...this.allRows];
            
            console.log('✓ CSV loaded:', this.allRows.length, 'pages');
            this.showLoadingState(false);
            
        } catch (error) {
            console.error('❌ CSV load failed:', error);
            this.showErrorState('Failed to load CSV data');
        }
    }

    // Determine page type based on URL and metadata
    determinePageType(row) {
        const url = row['Page URL'] || '';
        
        if (url.includes('blog/post-')) return 'Blog Post';
        if (url.includes('musical-poetry') || url.includes('life-is-your-word')) return 'Series Episode';
        if (url.includes('visualizations')) return 'Visualization';
        if (url.includes('about') || url.includes('resume_cv')) return 'About Page';
        if (url.includes('connect') || url.includes('legal-documents') || url.includes('terms')) return 'Utility Page';
        if (url.includes('amusements') || url.includes('games') || url.includes('shows')) return 'Content Hub';
        
        // Check page metadata for classification
        const pageTitle = row['Page Title'] || '';
        if (pageTitle.toLowerCase().includes('hub')) return 'Content Hub';
        if (pageTitle.toLowerCase().includes('mode')) return 'Content Page';
        
        return 'Content Page';
    }

    // Apply filters
    applyFilters() {
        let filtered = [...this.allRows];
        
        // Filter by page type
        if (this.filters.pageType !== 'all') {
            filtered = filtered.filter(row => row.pageType === this.filters.pageType);
        }
        
        // Filter by mobile responsive
        if (this.filters.mobile !== 'all') {
            if (this.filters.mobile === 'Yes') {
                filtered = filtered.filter(row => row['Mobile Responsive'] === 'Yes');
            } else if (this.filters.mobile === 'No') {
                filtered = filtered.filter(row => row['Mobile Responsive'] === 'No');
            }
        }
        
        // Filter by issues
        if (this.filters.issues !== 'all') {
            if (this.filters.issues === 'has-issues') {
                filtered = filtered.filter(row => row['Human Identified Issues'] && row['Human Identified Issues'].trim() !== '');
            } else if (this.filters.issues === 'no-issues') {
                filtered = filtered.filter(row => !row['Human Identified Issues'] || row['Human Identified Issues'].trim() === '');
            }
        }
        
        // Filter by search
        if (this.filters.search && this.filters.search.trim() !== '') {
            const searchLower = this.filters.search.toLowerCase().trim();
            filtered = filtered.filter(row => {
                const url = (row['Page URL'] || '').toLowerCase();
                const title = (row['Page Title'] || '').toLowerCase();
                return url.includes(searchLower) || title.includes(searchLower);
            });
        }
        
        this.filteredRows = filtered;
        console.log('✓ Filters applied:', this.filteredRows.length, 'pages');
    }

    // Sort table by column
    sortTable(column, direction = 'asc') {
        if (column === 'Page Title' || column === 'Page Type') {
            this.filteredRows.sort((a, b) => {
                const aVal = (a[column] || '').toLowerCase();
                const bVal = (b[column] || '').toLowerCase();
                if (aVal < bVal) return -1;
                if (aVal > bVal) return 1;
                return 0;
            });
        } else if (column === 'Inbound Links' || column === 'Outbound Links' || column === 'Date') {
            this.filteredRows.sort((a, b) => {
                const aVal = parseInt(a[column] || '0') || 0;
                const bVal = parseInt(b[column] || '0') || 0;
                if (direction === 'desc') {
                    return bVal - aVal;
                } else {
                    return aVal - bVal;
                }
            });
        } else if (column === 'Mobile Responsive') {
            const order = { 'Yes': 0, 'No': 1 };
            return this.filteredRows.sort((a, b) => {
                return order[a[column]] - order[b[column]];
            });
        }
    }

    // Render table
    renderTable() {
        const tbody = document.getElementById('table-body');
        
        if (this.filteredRows.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="table-cell text-center">
                        <div class="empty-state">
                            <div class="empty-state-icon">📂</div>
                            <p>No matching pages found</p>
                        </div>
                    </tr>
            `;
            return;
        }
        
        let html = '';
        
        this.filteredRows.forEach((row, index) => {
            const issuesCount = this.countIssues(row['Human Identified Issues']);
            const issuesBadge = issuesCount > 0 
                ? `<span class="badge ${issuesCount > 5 ? 'badge-danger' : 'badge-warning'}">${issuesCount}</span>` 
                : '';
            
            const responsiveBadge = row['Mobile Responsive'];
            const responsiveClass = responsiveBadge === 'Yes' ? 'badge-success' : 'badge-warning';
            const responsiveLabel = responsiveBadge === 'Yes' ? 'Yes' : 'No';
            
            html += `
                <tr ${this.selectedRow && this.selectedRow._id === row._id ? 'selected' : ''} data-row-id="${row._id}">
                    <td class="table-cell">${row['Page Type']}</td>
                    <td class="table-cell">
                        <span class="page-title" title="${row['Page Title']}">${row['Page Title']}</span>
                    </td>
                    <td class="table-cell">
                        <span class="links-count">${row['Inbound Links']} / ${row['Outbound Links']}</span>
                    </td>
                    <td class="table-cell text-center">${issuesBadge || ''}</td>
                    <td class="table-cell text-center">
                        <span class="${responsiveClass}">${responsiveLabel}</span>
                    </td>
                    <td class="table-cell">
                        <span class="date-value">${this.formatDate(row['Last Reviewed Date'])}</span>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        console.log('✓ Table rendered:', this.filteredRows.length, 'rows');
    }

    // Count issues in a row
    countIssues(issuesString) {
        if (!issuesString || issuesString.trim() === '') return 0;
        return issuesString.split(';').filter(issue => issue.trim() !== '').length;
    }

    // Format date for display
    formatDate(dateString) {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    }

    // Show/hide details panel
    showDetails(row) {
        const panel = document.getElementById('details-panel');
        const closeBtn = document.getElementById('close-panel');
        
        // Update selected row
        this.selectedRow = row;
        
        // Populate details panel
        this.populateDetailsPanel(row);
        
        // Show panel
        panel.classList.remove('hidden');
        panel.classList.add('visible');
        
        // Add click outside to close
        const closeHandler = (e) => {
            if (!panel.contains(e.target) && !panel.contains(e.target.closest('.details-panel'))) {
                this.hideDetails();
            }
        };
        
        document.addEventListener('click', closeHandler);
        closeBtn.addEventListener('click', this.hideDetails.bind(this));
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !panel.classList.contains('hidden')) {
                e.preventDefault();
                this.hideDetails();
            }
        });
    }

    // Hide details panel
    hideDetails() {
        const panel = document.getElementById('details-panel');
        panel.classList.remove('visible');
        panel.classList.add('hidden');
        this.selectedRow = null;
        
        // Remove table row highlighting
        document.querySelectorAll('.selected').forEach(row => {
            row.classList.remove('selected');
        });
    }

    // Populate details panel with page data
    populateDetailsPanel(row) {
        // Page metadata
        document.getElementById('metadata-template').textContent = row['Template Used'] || 'Not specified';
        document.getElementById('metadata-inbound').textContent = row['Inbound Links'] || '0';
        document.getElementById('metadata-outbound').textContent = row['Outbound Links'] || '0';
        
        // Embeds
        const video = row['Video Embed Working'];
        const audio = row['Audio Embed Working'];
        const images = row['Image Assets Loaded'];
        
        document.getElementById('metadata-video').textContent = video;
        document.getElementById('metadata-audio').textContent = audio;
        document.getElementById('metadata-images').textContent = images;
        
        // Issues
        const issuesList = document.getElementById('issues-list');
        issuesList.innerHTML = '';
        
        if (row['Human Identified Issues'] && row['Human Identified Issues'].trim()) {
            const issues = row['Human Identified Issues'].split(';');
            issues.forEach(issue => {
                const li = document.createElement('li');
                li.textContent = `• ${issue.trim()}`;
                issuesList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
                li.textContent = 'No issues detected';
            issuesList.appendChild(li);
        }
    }

    // Show loading state
    showLoadingState(showing) {
        const tbody = document.getElementById('table-body');
        const errorDiv = document.getElementById('screenshot-error');
        
        if (showing) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="table-cell text-center">
                        <div class="empty-state">
                            <div class="empty-state-icon">⏳</div>
                            <p>Loading data...</p>
                        </div>
                    </tr>
            `;
            errorDiv.style.display = 'none';
        } else {
            errorDiv.style.display = 'none';
            document.getElementById('screenshot-preview').style.display = 'none';
        }
    }

    // Show error state
    showErrorState(message) {
        const tbody = document.getElementById('table-body');
        tbody.innerHTML = `
            <tr>
                    <td colspan="5" class="table-cell text-center">
                        <div class="empty-state">
                            <div class="empty-state-icon">⚠️</div>
                            <p>${message}</p>
                        </div>
                    </tr>
            `;
    }

    // Setup event listeners
    setupEventListeners() {
        // Filter dropdowns
        document.getElementById('filter-page-type').addEventListener('change', (e) => {
            this.filters.pageType = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('filter-mobile').addEventListener('change', (e) => {
            this.filters.mobile = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('filter-issues').addEventListener('change', (e) => {
            this.filters.issues = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('search-input').addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                this.applyFilters();
            }, 300);
        });
        
        document.getElementById('search-input').addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                e.target.value = '';
                this.filters.search = '';
                this.applyFilters();
            }
        });
        
        // Clear filters button (not implemented yet)
        // document.getElementById('clear-filters').addEventListener('click', () => {
        //     this.filters.pageType = 'all';
        //     this.filters.mobile = 'all';
        //     this.filters.issues = 'all';
        //     this.filters.search = '';
        //     this.applyFilters();
        // });
    }

    // Screenshot loading
    loadScreenshot(pageUrl) {
        const screenshotDiv = document.getElementById('screenshot-preview');
        const errorDiv = document.getElementById('screenshot-error');
        
        // Convert page URL to filename
        const filename = this.convertPageToFilename(pageUrl);
        const screenshotPath = `../screenshots/${filename}`;
        
        screenshotDiv.innerHTML = `
            <div class="screenshot-error">
                <p>Screenshot not found</p>
            </div>
        `;
        
        // Load image
        const img = new Image();
        img.src = screenshotPath;
        img.onerror = () => {
            screenshotDiv.innerHTML = `
                <div class="screenshot-error">
                    <p>Failed to load screenshot</p>
                </div>
            `;
        };
        
        img.onload = () => {
            screenshotDiv.innerHTML = `<img src="${screenshotPath}" alt="Screenshot of ${pageUrl}">`;
        };
    }

    // Convert page URL to screenshot filename
    convertPageToFilename(pageUrl) {
        let filename = pageUrl.replace('.html', '');
        filename = filename.replace(/\//g, '_'); // Replace / with _
        filename = filename.replace(/_/g, '_'); // Replace multiple _ with single _
        while (filename.includes('__')) {
            filename = filename.replace('__', '_');
        }
        return filename + '.png';
    }
}

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', async () => {
    await this.init();
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('Application error:', e);
    console.error('Error details:', e.message, e.stack);
});
