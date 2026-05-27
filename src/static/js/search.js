/**
 * Balay & Beyond - Search Interactions
 * Manages global search input, redirection, and search history persistence.
 */

const SEARCH_STORAGE_KEY = 'balay_beyond_recent_searches';
const MIN_SEARCH_LENGTH = 2;

const SearchManager = {
    /**
     * Executes the search by redirecting the user to the shop view with a 'q' parameter.
     */
    processSearchQuery(rawQuery) {
        const cleanQuery = rawQuery.trim();
        
        if (cleanQuery.length < MIN_SEARCH_LENGTH) {
            return;
        }

        // Store in local history for a premium "Recent Searches" feel
        this.persistToHistory(cleanQuery);

        const targetUrl = new URL('/shop/', window.location.origin);
        targetUrl.searchParams.set('q', cleanQuery);
        
        window.location.href = targetUrl.toString();
    },

    /**
     * Maintains a list of the 5 most recent unique searches in localStorage.
     */
    persistToHistory(queryTerm) {
        try {
            const existingHistory = JSON.parse(localStorage.getItem(SEARCH_STORAGE_KEY) || '[]');
            const updatedHistory = [
                queryTerm, 
                ...existingHistory.filter(term => term !== queryTerm)
            ].slice(0, 5);
            
            localStorage.setItem(SEARCH_STORAGE_KEY, JSON.stringify(updatedHistory));
        } catch (storageError) {
            console.warn('[Search] Failed to update history:', storageError);
        }
    }
};

/**
 * Binds event listeners to the global search input defined in base.html.
 */
function initializeGlobalSearch() {
    const searchInputField = document.getElementById('collapsible-search-input');
    if (!searchInputField) return;

    // Handle 'Enter' key submission
    searchInputField.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            SearchManager.processSearchQuery(searchInputField.value);
        }
    });

    // UI Feedback: Focus effects
    searchInputField.addEventListener('focus', () => {
        const historyData = JSON.parse(localStorage.getItem(SEARCH_STORAGE_KEY) || '[]');
        if (historyData.length > 0) {
            // Future enhancement: Display a dropdown with recent searches here
            console.log('[Search] Suggestions available:', historyData);
        }
    });
}

// Auto-run on document ready
document.addEventListener('DOMContentLoaded', initializeGlobalSearch);

// Export for manual trigger if needed
window.SearchManager = SearchManager;
