/**
 * Balay & Beyond - Cart UI Logic
 * Manages frontend interactions for the shopping cart.
 */

const CART_BADGE_ID = 'cart-count-badge';

/**
 * Updates the cart count indicator in the navigation bar.
 */
function refreshCartBadge(newCount) {
    const badgeElement = document.getElementById(CART_BADGE_ID);
    if (badgeElement) {
        badgeElement.innerText = newCount;
        
        if (newCount > 0) {
            badgeElement.classList.remove('hidden');
        } else {
            badgeElement.classList.add('hidden');
        }
        
        // Subtle pulse animation for feedback
        badgeElement.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.2)' },
            { transform: 'scale(1)' }
        ], {
            duration: 300,
            easing: 'ease-out'
        });
    }
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
            // Note: Toast notification logic would go here if implemented in base.html
        }
    } catch (cartError) {
        console.error('[Cart] Addition failed:', cartError);
        alert('Unable to add item to your bag. Please try again.');
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
