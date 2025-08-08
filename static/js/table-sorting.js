// Table sorting functionality
function makeTableSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('th.sortable-header');
    let currentSort = {};
    
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;
            const type = header.dataset.type || 'text';
            
            // Toggle sort direction
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'asc';
            }
            
            // Update header classes
            headers.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            header.classList.add(`sort-${currentSort.direction}`);
            
            // Sort the table
            sortTable(table, column, currentSort.direction, type);
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
            return direction === 'asc' ? aValue - bValue : bValue - aValue;
        } else if (type === 'date') {
            return direction === 'asc' ? aValue - bValue : bValue - aValue;
        } else {
            const comparison = aValue.localeCompare(bValue);
            return direction === 'asc' ? comparison : -comparison;
        }
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

function getCellValue(row, column, type) {
    const cell = row.querySelector(`td[data-column="${column}"]`);
    if (!cell) return '';
    
    let value = cell.textContent.trim();
    
    if (type === 'number') {
        // Extract number from text (e.g., "€150" -> 150)
        const match = value.match(/[\d,]+\.?\d*/);
        return match ? parseFloat(match[0].replace(',', '')) : 0;
    } else if (type === 'date') {
        // Convert date string to timestamp
        const date = new Date(value);
        return isNaN(date.getTime()) ? 0 : date.getTime();
    }
    
    return value;
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
    
    // Initialize clickable rows
    initializeClickableRows();
});
