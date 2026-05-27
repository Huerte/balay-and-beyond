from decimal import Decimal
from apps.store.models import Product, Variant
from .models import Order, OrderItem


class CartService:
    def __init__(self, request):
        self.session = request.session
        session_cart = self.session.get('cart')
        if not session_cart:
            session_cart = self.session['cart'] = {}
        self.cart = session_cart

    def _get_cart_key(self, product_id, variant_id=None):
        if variant_id:
            return f"{product_id}_{variant_id}"
        return str(product_id)

    def add(self, product_id, quantity=1, variant_id=None):
        product_id = str(product_id)
        cart_key = self._get_cart_key(product_id, variant_id)
        
        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'product_id': product_id,
                'quantity': 0,
                'variant_id': str(variant_id) if variant_id else None
            }
            
        self.cart[cart_key]['quantity'] += int(quantity)
        self.save()

    def remove(self, product_id, variant_id=None):
        cart_key = self._get_cart_key(str(product_id), variant_id)
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def update(self, product_id, quantity, variant_id=None):
        cart_key = self._get_cart_key(str(product_id), variant_id)
        if cart_key in self.cart:
            self.cart[cart_key]['quantity'] = int(quantity)
            if self.cart[cart_key]['quantity'] <= 0:
                self.remove(product_id, variant_id)
            else:
                self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session['cart']
        self.save()

    def get_items(self):
        items = []
        for key, item in self.cart.items():
            try:
                product = Product.objects.get(id=item['product_id'])
                variant = Variant.objects.get(id=item['variant_id']) if item.get('variant_id') else None
                
                unit_price = product.price
                if variant:
                    unit_price += variant.price_modifier
                    
                items.append({
                    'product': product,
                    'variant': variant,
                    'quantity': item['quantity'],
                    'unit_price': unit_price,
                    'line_total': unit_price * item['quantity'],
                    'key': key
                })
            except (Product.DoesNotExist, Variant.DoesNotExist):
                pass
        return items

    def get_total(self):
        return sum(item['line_total'] for item in self.get_items())

    def get_count(self):
        return sum(item['quantity'] for item in self.cart.values())


def create_order_from_cart(user, cart_service, shipping_address, shipping_method, shipping_cost):
    cart_items = cart_service.get_items()
    if not cart_items:
        raise ValueError("Cannot create order from empty cart")
        
    subtotal = sum(item['line_total'] for item in cart_items)
    total = subtotal + Decimal(str(shipping_cost))
    
    order = Order.objects.create(
        user=user if user.is_authenticated else None,
        status='confirmed',
        total=total,
        shipping_address=shipping_address,
        shipping_method=shipping_method,
        shipping_cost=shipping_cost
    )
    
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            variant=item['variant'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            line_total=item['line_total']
        )
        
    cart_service.clear()
    return order

