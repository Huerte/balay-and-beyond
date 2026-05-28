from decimal import Decimal
from django.views import View
from django.shortcuts import redirect
from apps.orders.forms import CheckoutForm
from apps.orders.services import create_order_from_cart, CartService


SHIPPING_RATES = {
    'standard': Decimal('0.00'),
    'express':  Decimal('150.00'),
    'sameday':  Decimal('300.00'),
}


def _resolve_shipping_cost(shipping_method_label: str) -> Decimal:
    """Map the user-submitted shipping label to a server-side rate.
    Matches by substring so 'Standard (3-5 Days)' resolves to 'standard'.
    """
    label_lower = shipping_method_label.lower()
    for key, cost in SHIPPING_RATES.items():
        if key in label_lower:
            return cost
    return Decimal('0.00')


class ProcessPaymentView(View):
    """Mock payment handler. Always succeeds, never trusts client-posted prices."""

    def post(self, request):
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return redirect('orders:checkout')

        shipping_method = form.cleaned_data['shipping_method']
        shipping_cost = _resolve_shipping_cost(shipping_method)

        shipping_address = {
            'full_name': form.cleaned_data['full_name'],
            'street':    form.cleaned_data['street'],
            'city':      form.cleaned_data['city'],
            'province':  form.cleaned_data['province'],
            'zip_code':  form.cleaned_data['zip_code'],
            'country':   form.cleaned_data['country'],
        }

        cart_service = CartService(request)
        order = create_order_from_cart(
            user=request.user,
            cart_service=cart_service,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            shipping_cost=shipping_cost,
        )

        from django.urls import reverse
        url = reverse('orders:confirmation', kwargs={'order_id': order.id})
        return redirect(f'{url}?new=1')
