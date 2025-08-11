/**
 * Dashboard JavaScript - Enhanced functionality for the main dashboard
 */

class DashboardManager {
    constructor() {
        this.initializeTables();
        this.initializeRowInteractions();
        this.initializeSorting();
        this.initializeResponsiveBehavior();
    }

    /**
     * Initialize all data tables on the dashboard
     */
    initializeTables() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            this.setupTable(table);
        });
    }

    /**
     * Setup individual table with enhanced functionality
     */
    setupTable(table) {
        const tableId = table.id;
        const clickableRows = table.querySelectorAll('tr.clickable');
        
        clickableRows.forEach(row => {
            row.addEventListener('click', (e) => {
                // Don't trigger if clicking on links or buttons
                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || 
                    e.target.closest('a') || e.target.closest('button')) {
                    return;
                }
                
                this.handleRowClick(row, tableId);
            });
        });
    }

    /**
     * Handle row click events
     */
    handleRowClick(row, tableId) {
        const dataId = row.dataset[`${tableId.replace('-table', '')}Id`];
        
        if (!dataId) return;

        // Determine the appropriate URL based on table type
        let url;
        if (tableId === 'tradesmen-table') {
            url = `/tradesmen/${dataId}`;
        } else if (tableId === 'jobs-table') {
            // Check if it's a job or quote
            const iconElement = row.querySelector('.icon-circle i');
            if (iconElement && iconElement.classList.contains('fa-hammer')) {
                url = `/jobs/${dataId}`;
            } else {
                url = `/quotes/${dataId}`;
            }
        } else if (tableId === 'groups-table') {
            url = `/groups/${dataId}`;
        }

        if (url) {
            window.location.href = url;
        }
    }

    /**
     * Initialize row interaction effects
     */
    initializeRowInteractions() {
        const clickableRows = document.querySelectorAll('tr.clickable');
        
        clickableRows.forEach(row => {
            // Add hover effects
            row.addEventListener('mouseenter', () => {
                row.style.cursor = 'pointer';
            });
            
            // Add keyboard navigation
            row.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    row.click();
                }
            });
            
            // Make rows focusable for accessibility
            row.setAttribute('tabindex', '0');
            row.setAttribute('role', 'button');
            row.setAttribute('aria-label', 'Click to view details');
        });
    }

    /**
     * Initialize table sorting functionality
     */
    initializeSorting() {
        const sortableHeaders = document.querySelectorAll('.sortable-header');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleSort(header);
            });
        });
    }

    /**
     * Handle table sorting
     */
    handleSort(clickedHeader) {
        const table = clickedHeader.closest('table');
        const column = clickedHeader.dataset.column;
        const dataType = clickedHeader.dataset.type;
        const currentDirection = clickedHeader.dataset.sortDirection || 'none';
        
        // Clear previous sort indicators
        table.querySelectorAll('.sortable-header').forEach(h => {
            h.classList.remove('sort-asc', 'sort-desc');
            h.dataset.sortDirection = 'none';
        });
        
        // Determine new sort direction
        let newDirection;
        if (currentDirection === 'none' || currentDirection === 'desc') {
            newDirection = 'asc';
            clickedHeader.classList.add('sort-asc');
        } else {
            newDirection = 'desc';
            clickedHeader.classList.add('sort-desc');
        }
        
        clickedHeader.dataset.sortDirection = newDirection;
        
        // Sort the table
        this.sortTable(table, column, dataType, newDirection);
    }

    /**
     * Sort table data
     */
    sortTable(table, column, dataType, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = this.extractValue(a, column, dataType);
            const bValue = this.extractValue(b, column, dataType);
            
            let comparison = 0;
            
            if (dataType === 'number') {
                comparison = parseFloat(aValue) - parseFloat(bValue);
            } else if (dataType === 'date') {
                comparison = new Date(aValue) - new Date(bValue);
            } else {
                comparison = aValue.localeCompare(bValue);
            }
            
            return direction === 'asc' ? comparison : -comparison;
        });
        
        // Reorder rows in DOM
        rows.forEach(row => tbody.appendChild(row));
    }

    /**
     * Extract value from table cell for sorting
     */
    extractValue(row, column, dataType) {
        const cell = row.querySelector(`[data-column="${column}"]`);
        if (!cell) return '';
        
        let value = cell.textContent.trim();
        
        if (dataType === 'number') {
            // Extract numeric value, handling currency symbols
            value = value.replace(/[€£$,\s]/g, '');
            return parseFloat(value) || 0;
        } else if (dataType === 'date') {
            // Handle date formatting
            return value;
        }
        
        return value;
    }

    /**
     * Initialize responsive behavior
     */
    initializeResponsiveBehavior() {
        this.handleResize();
        window.addEventListener('resize', () => this.handleResize());
    }

    /**
     * Handle window resize for responsive adjustments
     */
    handleResize() {
        const isMobile = window.innerWidth <= 768;
        const tables = document.querySelectorAll('.table-responsive');
        
        tables.forEach(table => {
            if (isMobile) {
                table.classList.add('mobile-view');
            } else {
                table.classList.remove('mobile-view');
            }
        });
    }

    /**
     * Add loading states to buttons
     */
    addLoadingStates() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                if (button.classList.contains('btn--primary-large') || 
                    button.classList.contains('btn--icon')) {
                    this.showButtonLoading(button);
                }
            });
        });
    }

    /**
     * Show loading state for button
     */
    showButtonLoading(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        button.disabled = true;
        
        // Re-enable after a delay (simulating action completion)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }

    /**
     * Initialize search functionality
     */
    initializeSearch() {
        // Add search input to each section if needed
        const sections = document.querySelectorAll('.section-card');
        
        sections.forEach(section => {
            const title = section.querySelector('.section-title');
            if (title && title.textContent.includes('Search')) {
                this.addSearchInput(section);
            }
        });
    }

    /**
     * Add search input to section
     */
    addSearchInput(section) {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container mt-3';
        searchContainer.innerHTML = `
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Search..." aria-label="Search">
                <button class="btn btn-outline-secondary" type="button">
                    <i class="fas fa-search"></i>
                </button>
            </div>
        `;
        
        const tableContainer = section.querySelector('.table-responsive');
        if (tableContainer) {
            tableContainer.parentNode.insertBefore(searchContainer, tableContainer);
        }
    }
}

/**
 * Initialize dashboard when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardManager();
    
    // Add loading states
    dashboard.addLoadingStates();
    
    // Initialize search functionality
    dashboard.initializeSearch();
    
    console.log('Dashboard initialized successfully');
});

/**
 * Export for potential use in other modules
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}
