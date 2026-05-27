from .services import get_root_categories
from apps.orders.services import CartService
from .models import WishlistItem

def global_categories(request):
    """Injects top-level categories into every template context."""
    return {'categories': get_root_categories()}

def wishlist_context(request):
    """Injects the user's wishlist item count."""
    count = 0
    if request.user.is_authenticated:
        count = WishlistItem.objects.filter(user=request.user).count()
    return {'wishlist_count': count}

def cart_context(request):
    """Injects the current session cart item count."""
    cart_service = CartService(request)
    return {'cart_count': cart_service.get_count()}

