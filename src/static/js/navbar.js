/**
 * Balay & Beyond - Navbar Interactions
 * Handles the collapsible search bar.
 */

class NavbarManager {
    constructor() {
        // Search Elements
        this.searchToggle = document.getElementById('search-toggle-btn');
        this.searchWrapper = document.getElementById('search-input-wrapper');
        this.searchInput = document.getElementById('collapsible-search-input');
        this.searchClose = document.getElementById('search-close-btn');

        // State
        this.isSearchOpen = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // Search Toggle
        if (this.searchToggle) {
            this.searchToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openSearch();
            });
        }
        
        if (this.searchClose) {
            this.searchClose.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeSearch(true); // force close even if text exists
            });
        }

        // Global Clicks & Keys
        document.addEventListener('click', (e) => {
            if (this.isSearchOpen && !this.searchWrapper.contains(e.target) && !this.searchToggle.contains(e.target)) {
                this.closeSearch();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSearch(true);
            }
        });
        
        // Search blur (if clicked outside)
        if (this.searchInput) {
            this.searchInput.addEventListener('blur', () => {
                // Delay to allow clicks on search button or inside wrapper to register
                setTimeout(() => {
                    if (!this.searchWrapper.contains(document.activeElement)) {
                        this.closeSearch();
                    }
                }, 100);
            });
        }
    }

    openSearch() {
        if (this.isSearchOpen) return;
        this.isSearchOpen = true;
        this.searchWrapper.classList.remove('w-0', 'opacity-0', 'pointer-events-none');
        this.searchWrapper.classList.add('w-64', 'opacity-100', 'pointer-events-auto');
        // Wait for transition to start before focusing
        setTimeout(() => this.searchInput.focus(), 50);
    }

    closeSearch(force = false) {
        if (!this.isSearchOpen) return;
        if (!force && this.searchInput.value.trim() !== '') return; // Don't close if has text
        
        this.isSearchOpen = false;
        this.searchWrapper.classList.remove('w-64', 'opacity-100', 'pointer-events-auto');
        this.searchWrapper.classList.add('w-0', 'opacity-0', 'pointer-events-none');
        this.searchToggle.focus();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.navbarManager = new NavbarManager();
});
