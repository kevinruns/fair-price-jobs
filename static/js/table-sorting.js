// Table sorting functionality
function makeTableSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const headers = table.querySelectorAll('th.sortable-header');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;
            const type = header.dataset.type;
            const currentDirection = header.classList.contains('sort-asc') ? 'asc' : 
                                  header.classList.contains('sort-desc') ? 'desc' : 'none';
            
            // Clear all sort indicators
            headers.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Set new sort direction
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            header.classList.add(`sort-${newDirection}`);
            
            sortTable(table, column, newDirection, type);
        });
    });
}

function sortTable(table, column, direction, type) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = getCellValue(a, column, type);
        const bValue = getCellValue(b, column, type);
        
        if (type === 'number') {
            const aNum = parseFloat(aValue) || 0;
            const bNum = parseFloat(bValue) || 0;
            return direction === 'asc' ? aNum - bNum : bNum - aNum;
        } else if (type === 'date') {
            const aDate = new Date(aValue);
            const bDate = new Date(bValue);
            return direction === 'asc' ? aDate - bDate : bDate - aDate;
        } else {
            const comparison = aValue.localeCompare(bValue);
            return direction === 'asc' ? comparison : -comparison;
        }
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

function getCellValue(row, column, type) {
    const cell = row.querySelector(`[data-column="${column}"]`);
    if (!cell) return '';
    
    let value = cell.textContent.trim();
    
    // Clean up numeric values
    if (type === 'number') {
        value = value.replace(/[^\d.-]/g, '');
    }
    
    return value;
}

// Date formatting function
function formatDate(date) {
    if (!date) return "Date pending";
    return new Date(date).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// Number formatting function with thousand separators
function formatNumber(number) {
    if (!number) return "0";
    return parseInt(number).toLocaleString('en-GB');
}

// Handle clickable rows
function initializeClickableRows() {
    document.querySelectorAll('tr.clickable').forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on a link or button
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a') || e.target.closest('button')) {
                return;
            }
            // Find the first link in the row and navigate to it
            const link = this.querySelector('a');
            if (link) {
                window.location.href = link.href;
            }
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sorting for all sortable tables
    makeTableSortable('tradesmen-table');
    makeTableSortable('jobs-table');
    makeTableSortable('groups-table');
    makeTableSortable('jobs-search-table');
    makeTableSortable('tradesmen-search-table');

    // Initialize clickable rows
    initializeClickableRows();
    
    // Format all date cells
    formatAllDateCells();
    
    // Format all numeric cells
    formatAllNumericCells();
});

// Format all date cells on the page
function formatAllDateCells() {
    document.querySelectorAll('.date-cell').forEach(cell => {
        const dateValue = cell.dataset.date;
        
        if (dateValue) {
            cell.textContent = formatDate(dateValue);
        }
    });
}

// Format all numeric cells on the page
function formatAllNumericCells() {
    document.querySelectorAll('td.numeric').forEach(cell => {
        const text = cell.textContent.trim();
        // Check if it's a currency value (starts with €)
        if (text.startsWith('€')) {
            const number = text.substring(1); // Remove € symbol
            // Add thousand separators for euro values
            const formattedNumber = formatNumber(number);
            cell.textContent = `€${formattedNumber}`;
        } else if (/^\d+$/.test(text)) {
            // It's a plain number
            cell.textContent = formatNumber(text);
        }
    });
}
