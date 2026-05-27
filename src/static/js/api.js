/**
 * Balay & Beyond - Central API Handler
 * Encapsulates all AJAX/Fetch logic for the storefront.
 */

const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

const ENDPOINTS = {
    CART_ADD: '/cart/add/',
    CART_REMOVE: '/cart/remove/',
    CART_UPDATE: '/cart/update/',
    WISHLIST_TOGGLE: '/api/wishlist/toggle/',
};

/**
 * Internal helper to handle fetch responses and parse errors.
 */
async function processResponse(response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server returned ${response.status}`);
    }
    return response.json();
}

/**
 * Public API Interface
 */
const StoreAPI = {
    /**
     * Adds an item to the session cart.
     */
    async addToCart(productId, quantity = 1, variantId = null) {
        const payload = new FormData();
        payload.append('product_id', productId);
        payload.append('quantity', quantity);
        if (variantId) payload.append('variant_id', variantId);

        try {
            const response = await fetch(ENDPOINTS.CART_ADD, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN },
                body: payload
            });
            return await processResponse(response);
        } catch (fetchError) {
            console.error('[API] Add to cart failed:', fetchError);
            throw fetchError;
        }
    },

    /**
     * Removes an item from the session cart.
     */
    async removeFromCart(productId, variantId = null) {
        const payload = new FormData();
        payload.append('product_id', productId);
        if (variantId) payload.append('variant_id', variantId);

        try {
            const response = await fetch(ENDPOINTS.CART_REMOVE, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN },
                body: payload
            });
            return await processResponse(response);
        } catch (fetchError) {
            console.error('[API] Remove from cart failed:', fetchError);
            throw fetchError;
        }
    },

    /**
     * Updates the quantity of an item in the session cart.
     */
    async updateCartQuantity(productId, quantity, variantId = null) {
        const payload = new FormData();
        payload.append('product_id', productId);
        payload.append('quantity', quantity);
        if (variantId) payload.append('variant_id', variantId);

        try {
            const response = await fetch(ENDPOINTS.CART_UPDATE, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN },
                body: payload
            });
            return await processResponse(response);
        } catch (fetchError) {
            console.error('[API] Update cart quantity failed:', fetchError);
            throw fetchError;
        }
    },

    /**
     * Toggles an item in the user's wishlist.
     */
    async toggleWishlist(productId) {
        const payload = new FormData();
        payload.append('product_id', productId);

        try {
            const response = await fetch(ENDPOINTS.WISHLIST_TOGGLE, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN },
                body: payload
            });
            return await processResponse(response);
        } catch (fetchError) {
            console.error('[API] Toggle wishlist failed:', fetchError);
            throw fetchError;
        }
    }
};

// Expose globally for use in templates and other scripts
window.StoreAPI = StoreAPI;
window.cartApi = {
    add: (productId, quantity = 1, variantId = null) => StoreAPI.addToCart(productId, quantity, variantId)
};
