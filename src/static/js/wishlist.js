/**
 * Balay & Beyond - Wishlist Interactions
 * Handles optimistic UI updates for wishlist toggles across the site.
 */

document.addEventListener('DOMContentLoaded', () => {
    const wishlistButtons = document.querySelectorAll('[data-wishlist-btn]');
    const badge = document.getElementById('wishlist-count-badge');

    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast-message pointer-events-auto flex items-center p-4 mb-2 text-surface rounded shadow-md transition-opacity duration-300 ${type === 'error' ? 'bg-danger' : (type === 'success' ? 'bg-accent' : 'bg-muted')}`;
        toast.setAttribute('role', 'alert');

        const iconType = type === 'error' ? 'alert-circle' : (type === 'success' ? 'check-circle' : 'info');
        
        toast.innerHTML = `
            <div class="mr-3">
                <i data-lucide="${iconType}" class="w-5 h-5"></i>
            </div>
            <div class="text-sm font-medium">${message}</div>
            <button type="button" class="ml-4 flex-shrink-0 text-surface/80 hover:text-surface focus:outline-none" onclick="this.parentElement.remove();">
                <span class="sr-only">Close</span>
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        `;
        
        container.appendChild(toast);
        if (window.lucide) lucide.createIcons();

        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    wishlistButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.getAttribute('data-product-id');
            const icon = btn.querySelector('svg, i');
            
            if (!productId || !window.StoreAPI || !icon) return;

            // Optimistic UI toggle
            const isAdded = icon.classList.contains('fill-danger');
            
            try {
                const response = await window.StoreAPI.toggleWishlist(productId);
                
                // Update badge count globally
                if (badge !== undefined && response.count !== undefined) {
                    badge.textContent = response.count;
                    if (response.count > 0) {
                        badge.classList.remove('hidden');
                        badge.animate([
                            { transform: 'scale(1)' },
                            { transform: 'scale(1.4)' },
                            { transform: 'scale(1)' }
                        ], { duration: 300, easing: 'ease-out' });
                    } else {
                        badge.classList.add('hidden');
                    }
                }
                
                if (response.status === 'added') {
                    // Make heart solid
                    icon.classList.add('fill-danger', 'text-danger');
                    icon.classList.remove('text-muted');
                    btn.classList.add('border-danger');
                } else if (response.status === 'removed') {
                    // Make heart outline
                    icon.classList.remove('fill-danger', 'text-danger');
                    icon.classList.add('text-muted');
                    btn.classList.remove('border-danger');
                }

            } catch (error) {
                // If it's a 401 error, we show a toast advising them to login
                if (error.message.includes('401') || error.message.includes('Authentication')) {
                    showToast('Please log in to save items to your wishlist.', 'info');
                } else {
                    showToast('Failed to update wishlist. Please try again.', 'error');
                }
            }
        });
    });
});
