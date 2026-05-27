import os
from django.conf import settings
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
import json
from .models import Review, WishlistItem, Product
from . import services


def _get_hero_images():
    """Return static URLs for every image inside static/assets/images/hero/.

    Add any .jpg/.jpeg/.png/.webp/.avif file to that folder and it will be
    served automatically. The folder is sorted alphabetically so filenames
    control display order (hero1.jpg, hero2.jpg, …).
    """
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.avif'}
    urls = []
    # STATICFILES_DIRS[0] is BASE_DIR / 'static'
    hero_dir = os.path.join(settings.STATICFILES_DIRS[0], 'assets', 'images', 'hero')
    if os.path.isdir(hero_dir):
        for fname in sorted(os.listdir(hero_dir)):
            if os.path.splitext(fname)[1].lower() in extensions:
                urls.append(f"{settings.STATIC_URL}assets/images/hero/{fname}")
    return urls


class HomeView(TemplateView):
    template_name = 'store/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = services.get_featured_products()
        context['categories'] = services.get_root_categories()
        context['hero_images'] = _get_hero_images()
        return context


class ShopView(ListView):
    template_name = 'store/shop.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        from .models import Category
        qs = services.get_published_products()

        # Category filter
        category_slug = self.request.GET.get('category', '').strip()
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # Search
        search_term = self.request.GET.get('q', '').strip()
        if search_term:
            qs = qs.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )

        # Price filter — supports multiple values: ?price=under_1000&price=over_5000
        price_filters = self.request.GET.getlist('price')
        if price_filters:
            price_q = Q()
            for pf in price_filters:
                if pf == 'under_1000':
                    price_q |= Q(price__lt=1000)
                elif pf == '1000_5000':
                    price_q |= Q(price__gte=1000, price__lte=5000)
                elif pf == 'over_5000':
                    price_q |= Q(price__gt=5000)
            qs = qs.filter(price_q)

        # In-stock filter
        if self.request.GET.get('in_stock') == '1':
            qs = qs.filter(stock__gt=0)

        # Sort
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_low':
            qs = qs.order_by('price')
        elif sort == 'price_high':
            qs = qs.order_by('-price')
        elif sort == 'name':
            qs = qs.order_by('name')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        from .models import Category
        from urllib.parse import urlencode

        context = super().get_context_data(**kwargs)

        # --- Active filter state ---
        category_slug = self.request.GET.get('category', '').strip()
        active_category = None
        if category_slug:
            try:
                active_category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                category_slug = ''

        active_sort = self.request.GET.get('sort', 'newest')
        active_prices = self.request.GET.getlist('price')
        active_in_stock = self.request.GET.get('in_stock', '')
        search_query = self.request.GET.get('q', '').strip()

        context['active_category'] = active_category
        context['active_category_slug'] = category_slug
        context['active_sort'] = active_sort
        context['active_prices'] = active_prices
        context['active_in_stock'] = active_in_stock
        context['search_query'] = search_query

        # Count non-default active filters (sort excluded — it always has a value)
        filter_count = (
            (1 if category_slug else 0)
            + len(active_prices)
            + (1 if active_in_stock == '1' else 0)
        )
        context['active_filter_count'] = filter_count

        # Build a query string of current filters WITHOUT the page param so
        # pagination links can append &page=N cleanly.
        qs_params = {}
        if category_slug:
            qs_params['category'] = category_slug
        if active_sort and active_sort != 'newest':
            qs_params['sort'] = active_sort
        if active_prices:
            qs_params['price'] = active_prices  # urlencode handles lists with doseq
        if active_in_stock == '1':
            qs_params['in_stock'] = '1'
        if search_query:
            qs_params['q'] = search_query
        context['filter_qs'] = urlencode(qs_params, doseq=True)

        context['categories'] = services.get_root_categories()
        return context


class CategoryRedirectView(View):
    """Backward-compat redirect: /shop/category/<slug>/ → /shop/?category=<slug>."""

    def get(self, request, slug):
        from django.urls import reverse
        target = reverse('store:shop') + f'?category={slug}'
        return redirect(target, permanent=True)



class ProductDetailView(DetailView):
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        return services.get_product_by_slug(self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['product_images'] = product.images.all()
        context['related_products'] = services.get_published_products().filter(
            category=product.category
        ).exclude(pk=product.pk)[:4]
        
        if self.request.user.is_authenticated:
            context['in_wishlist'] = WishlistItem.objects.filter(user=self.request.user, product=product).exists()
        else:
            context['in_wishlist'] = False
            
        return context


class SubmitReviewView(LoginRequiredMixin, View):
    def post(self, request, slug):
        product = services.get_product_by_slug(slug)
        rating = request.POST.get('rating')
        body = request.POST.get('body', '')
        
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': int(rating), 'body': body}
            )
            
        return redirect('store:product_detail', slug=slug)


class ContactView(TemplateView):
    template_name = 'store/support/contact.html'

class ShippingReturnsView(TemplateView):
    template_name = 'store/support/shipping.html'

class FAQView(TemplateView):
    template_name = 'store/support/faq.html'

class CareGuideView(TemplateView):
    template_name = 'store/support/care_guide.html'


class AboutView(TemplateView):
    template_name = 'store/about.html'


class PrivacyView(TemplateView):
    template_name = 'store/privacy.html'


class TermsView(TemplateView):
    template_name = 'store/terms.html'


class WishlistView(LoginRequiredMixin, ListView):
    template_name = 'store/wishlist.html'
    context_object_name = 'wishlist_items'
    paginate_by = 12

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('product')


class ToggleWishlistView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'Product ID required'}, status=400)
            
        try:
            product = Product.objects.get(id=product_id)
            item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
            
            if not created:
                item.delete()
                status = 'removed'
            else:
                status = 'added'
                
            count = WishlistItem.objects.filter(user=request.user).count()
            return JsonResponse({'status': status, 'count': count})
            
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
