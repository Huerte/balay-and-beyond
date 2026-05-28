from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import CartService
from .models import Order


class CartView(TemplateView):
    template_name = 'orders/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartService(self.request)
        context['cart_items'] = cart.get_items()
        context['cart_total'] = cart.get_total()
        return context


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        variant_id = request.POST.get('variant_id')
        
        if not product_id:
            return JsonResponse({'ok': False, 'error': 'product_id required'}, status=400)
            
        cart = CartService(request)
        cart.add(product_id, quantity, variant_id)
        
        return JsonResponse({'ok': True, 'cart_count': cart.get_count()})


class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        
        if not product_id:
            return JsonResponse({'ok': False, 'error': 'product_id required'}, status=400)
            
        cart = CartService(request)
        cart.remove(product_id, variant_id)
        
        return JsonResponse({
            'ok': True, 
            'cart_count': cart.get_count(),
            'subtotal': cart.get_total()
        })


class UpdateCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        variant_id = request.POST.get('variant_id')
        
        if not product_id or quantity is None:
            return JsonResponse({'ok': False, 'error': 'product_id and quantity required'}, status=400)
            
        cart = CartService(request)
        cart.update(product_id, quantity, variant_id)
        
        line_total = 0
        for item in cart.get_items():
            item_variant_id = str(item['variant'].id) if item['variant'] else None
            if str(item['product'].id) == str(product_id) and item_variant_id == str(variant_id):
                line_total = item['line_total']
                break
                
        return JsonResponse({
            'ok': True,
            'line_total': line_total,
            'cart_total': cart.get_total(),
            'cart_count': cart.get_count()
        })


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/checkout.html'

    def dispatch(self, request, *args, **kwargs):
        cart = CartService(request)
        if cart.get_count() == 0:
            return redirect('orders:cart')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartService(self.request)
        context['cart_items'] = cart.get_items()
        context['cart_total'] = cart.get_total()
        context['addresses'] = self.request.user.addresses.all()
        return context


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    template_name = 'orders/confirmation.html'
    context_object_name = 'order'
    
    def get_object(self):
        from django.db.models import Prefetch
        from apps.store.models import Review
        return get_object_or_404(
            Order.objects.prefetch_related(
                Prefetch('line_items__product__reviews', queryset=Review.objects.filter(user=self.request.user), to_attr='user_reviews')
            ), 
            id=self.kwargs['order_id'], 
            user=self.request.user
        )
        
    def get_context_data(self, **kwargs):
        from django.conf import settings
        context = super().get_context_data(**kwargs)
        order = self.object

        # Detect whether the user just completed payment or is viewing an existing order
        context['is_new_order'] = self.request.GET.get('new') == '1'
        context['order_subtotal'] = order.total - order.shipping_cost
        context['support_email'] = getattr(settings, 'SUPPORT_EMAIL', 'support@balaybeyond.com')

        # Clear the notification highlight for this order now that the user has seen it
        if order.has_unread_update:
            order.has_unread_update = False
            order.save(update_fields=['has_unread_update'])
            # Also clear the nav dot if no other orders are still flagged
            remaining = order.user.orders.filter(has_unread_update=True).exists()
            if not remaining and order.user.has_unread_orders:
                order.user.has_unread_orders = False
                order.user.save(update_fields=['has_unread_orders'])

        return context


class OrderHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/history.html'
    
    def get_context_data(self, **kwargs):
        from django.db.models import Prefetch
        from apps.store.models import Review
        
        # Snapshot IDs FIRST, then reset — queryset must be evaluated before update()
        updated_order_ids = list(
            Order.objects.filter(user=self.request.user, has_unread_update=True)
            .values_list('id', flat=True)
        )

        # Reset per-order flags now that we have the IDs
        if updated_order_ids:
            Order.objects.filter(id__in=updated_order_ids).update(has_unread_update=False)

        context = super().get_context_data(**kwargs)
        all_orders = Order.objects.filter(user=self.request.user).order_by('-created_at').prefetch_related(
            'line_items__product',
            Prefetch('line_items__product__reviews', queryset=Review.objects.filter(user=self.request.user), to_attr='user_reviews')
        )
        
        context['in_progress_orders'] = all_orders.exclude(status='delivered')
        context['delivered_orders'] = all_orders.filter(status='delivered')
        context['updated_order_ids'] = updated_order_ids
        return context
