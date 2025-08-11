"""
Dashboard Configuration
Contains all configurable settings for the dashboard functionality
"""

# Dashboard Layout Settings
DASHBOARD_CONFIG = {
    'max_items_per_section': 10,
    'refresh_interval': 300,  # 5 minutes in seconds
    'enable_auto_refresh': False,
    'show_empty_sections': True,
    'enable_search': True,
    'enable_sorting': True,
    'enable_pagination': False,
}

# Section Card Variants
SECTION_VARIANTS = {
    'tradesmen': 'light',
    'jobs': 'white',
    'groups': 'light',
}

# Table Configuration
TABLE_CONFIG = {
    'tradesmen': {
        'columns': [
            {'column': 'avatar', 'type': 'text', 'label': '', 'sortable': False},
            {'column': 'name', 'type': 'text', 'label': 'Name', 'sortable': True},
            {'column': 'company', 'type': 'text', 'label': 'Company', 'sortable': True},
            {'column': 'trade', 'type': 'text', 'label': 'Trade', 'sortable': True},
            {'column': 'rating', 'type': 'number', 'label': 'Rating', 'sortable': True},
            {'column': 'jobs', 'type': 'number', 'label': 'Jobs', 'sortable': True, 'numeric': True},
            {'column': 'quotes', 'type': 'number', 'label': 'Quotes', 'sortable': True, 'numeric': True},
            {'column': 'added_by', 'type': 'text', 'label': 'Added By', 'sortable': True},
        ],
        'default_sort': 'rating',
        'default_order': 'desc',
        'empty_message': 'No rated tradesmen found. Top-rated tradesmen will appear here when you or your group members add tradesmen and complete jobs with ratings.'
    },
    'jobs': {
        'columns': [
            {'column': 'icon', 'type': 'text', 'label': '', 'sortable': False},
            {'column': 'title', 'type': 'text', 'label': 'Title', 'sortable': True},
            {'column': 'tradesman', 'type': 'text', 'label': 'Tradesman', 'sortable': True},
            {'column': 'trade', 'type': 'text', 'label': 'Trade', 'sortable': True},
            {'column': 'date', 'type': 'date', 'label': 'Date', 'sortable': True},
            {'column': 'cost', 'type': 'number', 'label': 'Price', 'sortable': True, 'numeric': True},
            {'column': 'rating', 'type': 'number', 'label': 'Rating', 'sortable': True},
            {'column': 'added_by', 'type': 'text', 'label': 'Added By', 'sortable': True},
        ],
        'default_sort': 'date',
        'default_order': 'desc',
        'empty_message': 'No recently completed jobs found. Jobs will appear here when you or members of your groups complete work with tradesmen.'
    },
    'groups': {
        'columns': [
            {'column': 'icon', 'type': 'text', 'label': '', 'sortable': False},
            {'column': 'name', 'type': 'text', 'label': 'Group Name', 'sortable': True},
            {'column': 'postcode', 'type': 'text', 'label': 'Postcode', 'sortable': True},
            {'column': 'members', 'type': 'number', 'label': 'Members', 'sortable': True, 'numeric': True},
            {'column': 'status', 'type': 'text', 'label': 'Your Status', 'sortable': True},
        ],
        'default_sort': 'name',
        'default_order': 'asc',
        'empty_message': 'You haven\'t joined any groups yet. Join or create groups to collaborate with others and share tradesmen recommendations.'
    }
}

# Button Configuration
BUTTON_CONFIG = {
    'primary_large': {
        'width': '220px',
        'height': '36px',
        'font_size': '16px',
        'border_radius': '8px',
    },
    'icon': {
        'width': '36px',
        'height': '36px',
        'font_size': '20px',
        'border_radius': '8px',
    }
}

# Responsive Breakpoints
RESPONSIVE_BREAKPOINTS = {
    'mobile': 480,
    'tablet': 768,
    'desktop': 1200,
    'large_desktop': 1400,
}

# Animation Settings
ANIMATION_CONFIG = {
    'hover_scale': 1.05,
    'hover_transition': '0.2s ease',
    'card_hover_lift': '2px',
    'row_hover_lift': '1px',
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'enable_lazy_loading': True,
    'enable_virtual_scrolling': False,
    'max_visible_rows': 50,
    'debounce_delay': 300,
}

# Accessibility Settings
ACCESSIBILITY_CONFIG = {
    'enable_keyboard_navigation': True,
    'enable_screen_reader_support': True,
    'enable_high_contrast_mode': False,
    'enable_reduced_motion': False,
}

# Search Configuration
SEARCH_CONFIG = {
    'enable_global_search': True,
    'enable_section_search': True,
    'search_delay': 500,
    'min_search_length': 2,
    'max_search_results': 100,
}

# Export Configuration
EXPORT_CONFIG = {
    'enable_csv_export': True,
    'enable_pdf_export': False,
    'enable_excel_export': False,
    'max_export_rows': 1000,
}
