/**
 * Balay & Beyond - Checkout Flow Logic
 * Manages the multi-step checkout process and mock payment simulation.
 */

const CHECKOUT_STATE = {
    currentStep: 1,
    shippingCost: 0,
    shippingName: 'Standard (3-5 Days)'
};

const UI_SELECTORS = {
    OVERLAY: 'processing-overlay',
    SUBMISSION_FORM: 'final-checkout-form',
    TOTAL_PRICE: 'summary-total',
    SHIPPING_NAME: 'summary-shipping-name',
    SHIPPING_PRICE: 'summary-shipping-cost'
};

/**
 * Validates inputs for the current active step.
 */
function validateActiveStep(stepIndex) {
    if (stepIndex === 1) {
        const shippingFields = ['email', 'full_name', 'street', 'city', 'province', 'zip_code'];
        let isDataValid = true;
        
        shippingFields.forEach(fieldId => {
            const inputNode = document.getElementById(fieldId);
            if (!inputNode || !inputNode.value.trim()) {
                inputNode?.classList.add('border-danger');
                isDataValid = false;
            } else {
                inputNode?.classList.remove('border-danger');
            }
        });
        return isDataValid;
    }
    
    if (stepIndex === 3) {
        const cardFields = ['card_number', 'card_expiry', 'card_cvv', 'card_name'];
        return cardFields.every(id => document.getElementById(id)?.value.trim().length > 0);
    }
    
    return true;
}

/**
 * Updates the 1-2-3 progress indicators at the top of the checkout.
 */
function refreshProgressIndicators(targetStep) {
    for (let i = 1; i <= 3; i++) {
        const indicatorNode = document.getElementById(`indicator-${i}`);
        if (!indicatorNode) continue;
        
        const statusCircle = indicatorNode.querySelector('div');
        const statusLabel = indicatorNode.querySelector('span');
        
        if (i < targetStep) { // Previous Step (Completed)
            statusCircle.className = 'w-10 h-10 rounded-full flex items-center justify-center bg-accent text-surface border-2 border-accent transition-all';
            statusCircle.innerHTML = '<i data-lucide="check" class="w-5 h-5"></i>';
            statusLabel.className = 'text-[10px] uppercase tracking-widest font-bold text-accent';
        } else if (i === targetStep) { // Active Step
            statusCircle.className = 'w-10 h-10 rounded-full flex items-center justify-center bg-primary text-surface border-2 border-primary transition-all';
            statusCircle.innerHTML = i;
            statusLabel.className = 'text-[10px] uppercase tracking-widest font-bold text-text';
        } else { // Future Step
            statusCircle.className = 'w-10 h-10 rounded-full flex items-center justify-center bg-surface text-muted border-2 border-muted/20 transition-all';
            statusCircle.innerHTML = i;
            statusLabel.className = 'text-[10px] uppercase tracking-widest font-bold text-muted';
        }
    }
    if (window.lucide) window.lucide.createIcons();
}

/**
 * Handles navigation between checkout sections.
 */
function switchCheckoutStep(targetStep) {
    // Only validate when moving forward
    if (targetStep > CHECKOUT_STATE.currentStep && !validateActiveStep(CHECKOUT_STATE.currentStep)) {
        return; 
    }

    const currentSection = document.getElementById(`step-${CHECKOUT_STATE.currentStep}`);
    const targetSection = document.getElementById(`step-${targetStep}`);
    
    if (currentSection && targetSection) {
        currentSection.classList.add('hidden');
        targetSection.classList.remove('hidden');
        
        refreshProgressIndicators(targetStep);
        CHECKOUT_STATE.currentStep = targetStep;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Updates the order total based on the selected shipping method.
 */
function refreshShippingSummary(fee, label) {
    CHECKOUT_STATE.shippingCost = parseFloat(fee);
    CHECKOUT_STATE.shippingName = label;
    
    const nameNode = document.getElementById(UI_SELECTORS.SHIPPING_NAME);
    const costNode = document.getElementById(UI_SELECTORS.SHIPPING_PRICE);
    const totalNode = document.getElementById(UI_SELECTORS.TOTAL_PRICE);
    
    if (nameNode) nameNode.innerText = label.split(' ')[0];
    if (costNode) costNode.innerText = `₱${fee.toFixed(2)}`;
    
    if (totalNode) {
        const cartSubtotal = parseFloat(totalNode.dataset.base);
        const checkoutTotal = cartSubtotal + CHECKOUT_STATE.shippingCost;
        totalNode.innerText = `₱${checkoutTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
    }
}

/**
 * Orchestrates the mock payment simulation and form submission.
 */
function runMockPaymentProcess() {
    if (!validateActiveStep(3)) {
        alert('Please fill in the demo payment details to proceed.');
        return;
    }

    const overlayNode = document.getElementById(UI_SELECTORS.OVERLAY);
    if (overlayNode) overlayNode.classList.remove('hidden');

    // Sync UI fields to the hidden POST form
    const syncMap = {
        'full_name': 'final-full-name',
        'street': 'final-street',
        'city': 'final-city',
        'province': 'final-province',
        'zip_code': 'final-zip-code',
        'country': 'final-country-val'
    };

    Object.entries(syncMap).forEach(([uiId, hiddenId]) => {
        const uiInput = document.getElementById(uiId);
        const hiddenInput = document.getElementById(hiddenId);
        if (uiInput && hiddenInput) hiddenInput.value = uiInput.value;
    });

    // Add shipping data
    document.getElementById('final-shipping-method').value = CHECKOUT_STATE.shippingName;
    document.getElementById('final-shipping-cost-val').value = CHECKOUT_STATE.shippingCost;

    // Simulate a 1.5s delay to make the "payment" feel real
    setTimeout(() => {
        const submissionForm = document.getElementById(UI_SELECTORS.SUBMISSION_FORM);
        if (submissionForm) submissionForm.submit();
    }, 1500);
}

/**
 * Setup input masks for better UX on card fields.
 */
function configureInputMasks() {
    const cardInput = document.getElementById('card_number');
    const expiryInput = document.getElementById('card_expiry');
    
    if (cardInput) {
        cardInput.addEventListener('input', (event) => {
            event.target.value = event.target.value
                .replace(/[^\d]/g, '')
                .replace(/(.{4})/g, '$1 ')
                .trim();
        });
    }
    
    if (expiryInput) {
        expiryInput.addEventListener('input', (event) => {
            event.target.value = event.target.value
                .replace(/[^\d]/g, '')
                .replace(/(.{2})/, '$1/')
                .trim();
        });
    }
}

// Expose public methods for use in template event handlers
window.CheckoutController = {
    step: switchCheckoutStep,
    shipping: refreshShippingSummary,
    pay: runMockPaymentProcess
};

// Auto-init masks when the DOM is ready
document.addEventListener('DOMContentLoaded', configureInputMasks);
