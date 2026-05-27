/**
 * Balay & Beyond - Cart UI Logic
 * Manages frontend interactions for the shopping cart.
 */

const CART_BADGE_ID = 'cart-count-badge';

/**
 * Updates the cart count badge. Never shows a 0.
 */
function refreshCartBadge(newCount) {
    const badgeElement = document.getElementById(CART_BADGE_ID);
    if (!badgeElement) return;

    badgeElement.innerText = newCount;
    if (newCount > 0) {
        badgeElement.classList.remove('hidden');
        badgeElement.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.4)' },
            { transform: 'scale(1)' }
        ], { duration: 300, easing: 'ease-out' });
    } else {
        badgeElement.classList.add('hidden');
    }
}

/**
 * Shows a lightweight toast notification.
 */
function showCartToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const colors = { success: 'bg-accent', error: 'bg-danger', info: 'bg-muted' };
    const icons  = { success: 'check-circle', error: 'alert-circle', info: 'info' };

    const toast = document.createElement('div');
    toast.className = `toast-message pointer-events-auto flex items-center p-4 mb-2 text-surface rounded shadow-md transition-opacity duration-300 ${colors[type]}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="mr-3"><i data-lucide="${icons[type]}" class="w-5 h-5"></i></div>
        <div class="text-sm font-medium">${message}</div>
        <button type="button" class="ml-4 flex-shrink-0 text-surface/80 hover:text-surface" onclick="this.parentElement.remove();">
            <i data-lucide="x" class="w-4 h-4"></i>
        </button>
    `;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Universal handler for adding products to the cart from any page.
 */
async function performAddToCart(productId, itemQuantity = 1, variantId = null, triggerButton = null) {
    const originalContent = triggerButton ? triggerButton.innerHTML : '';
    
    if (triggerButton) {
        triggerButton.disabled = true;
        triggerButton.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin mx-auto"></i>';
        if (window.lucide) window.lucide.createIcons();
    }

    try {
        const cartResponse = await window.StoreAPI.addToCart(productId, itemQuantity, variantId);
        if (cartResponse.ok) {
            refreshCartBadge(cartResponse.cart_count);
            showCartToast('Item added to your bag!');
        }
    } catch (cartError) {
        console.error('[Cart] Addition failed:', cartError);
        showCartToast('Unable to add item. Please try again.', 'error');
    } finally {
        if (triggerButton) {
            triggerButton.disabled = false;
            triggerButton.innerHTML = originalContent;
            if (window.lucide) window.lucide.createIcons();
        }
    }
}

/**
 * Logic specific to the /cart/ page view.
 */
const CartUI = {
    /**
     * Increments or decrements item quantity and updates the DOM.
     */
    async adjustQuantity(productId, variantId, quantityDelta, itemKey) {
        const quantityInput = document.getElementById(`qty-${itemKey}`);
        const targetQuantity = parseInt(quantityInput.value) + quantityDelta;
        
        if (targetQuantity < 1) return;

        const itemRow = document.getElementById(`cart-item-${itemKey}`);
        itemRow.style.opacity = '0.5';
        itemRow.style.pointerEvents = 'none';

        try {
            const updateResponse = await window.StoreAPI.updateCartQuantity(productId, targetQuantity, variantId);
            if (updateResponse.ok) {
                quantityInput.value = targetQuantity;
                
                // Update price displays
                document.getElementById(`total-${itemKey}`).innerText = `₱${updateResponse.line_total.toFixed(2)}`;
                document.getElementById('cart-subtotal').innerText = `₱${updateResponse.cart_total.toFixed(2)}`;
                document.getElementById('cart-total').innerText = `₱${updateResponse.cart_total.toFixed(2)}`;
                
                refreshCartBadge(updateResponse.cart_count);
            }
        } catch (updateError) {
            console.error('[Cart] Quantity update failed:', updateError);
        } finally {
            itemRow.style.opacity = '1';
            itemRow.style.pointerEvents = 'auto';
        }
    },

    /**
     * Removes an item row from the cart and updates totals.
     */
    async deleteItem(productId, variantId, itemKey) {
        const itemRow = document.getElementById(`cart-item-${itemKey}`);
        itemRow.style.opacity = '0.2';
        itemRow.style.pointerEvents = 'none';

        try {
            const deleteResponse = await window.StoreAPI.removeFromCart(productId, variantId);
            if (deleteResponse.ok) {
                itemRow.style.transform = 'scale(0.95)';
                itemRow.style.transition = 'all 0.2s ease-out';
                
                setTimeout(() => {
                    itemRow.remove();
                    if (deleteResponse.cart_count === 0) {
                        window.location.reload(); // Switch to empty state template
                    } else {
                        document.getElementById('cart-subtotal').innerText = `₱${deleteResponse.subtotal.toFixed(2)}`;
                        document.getElementById('cart-total').innerText = `₱${deleteResponse.subtotal.toFixed(2)}`;
                        refreshCartBadge(deleteResponse.cart_count);
                    }
                }, 200);
            }
        } catch (deleteError) {
            console.error('[Cart] Item removal failed:', deleteError);
            itemRow.style.opacity = '1';
            itemRow.style.pointerEvents = 'auto';
        }
    }
};

// Expose handlers to global scope for HTML onclick attributes
window.handleAddToCart = performAddToCart;
window.CartUI = CartUI;
