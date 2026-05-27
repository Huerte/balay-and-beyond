from django.contrib import admin
from django.utils.text import slugify
import uuid
import re
from .models import Category, Product, ProductImage, Variant, Review, WishlistItem


def _generate_sku(name, category_name):
    """Generate a deterministic, human-readable SKU.

    Format: BB-<CAT>-<NAME>-<XXXX>
    Example: BB-KIT-CERAMIC-MUG-A3F9
    """
    def _initials(text, max_chars=8):
        # Take the first letter of each word, uppercase, max max_chars
        words = re.sub(r'[^a-zA-Z0-9 ]', '', text).split()
        condensed = ''.join(w[:3].upper() for w in words)
        return condensed[:max_chars]

    cat_part = _initials(category_name, 6)
    name_part = _initials(name, 10)
    uid_part = uuid.uuid4().hex[:4].upper()
    return f"BB-{cat_part}-{name_part}-{uid_part}"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_published', 'sku', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, VariantInline]
    readonly_fields = ('sku',)

    def get_exclude(self, request, obj=None):
        # Completely hide the SKU field when adding a new product.
        # It will still show up as a read-only field when editing.
        if not obj:
            return ('sku',)
        return super().get_exclude(request, obj)

    def save_model(self, request, obj, form, change):
        # Only generate on creation, never overwrite an existing SKU.
        if not change and not obj.sku:
            category_name = obj.category.name if obj.category_id else 'GEN'
            sku = _generate_sku(obj.name, category_name)
            # Ensure uniqueness — retry with a fresh UUID suffix if there's a collision.
            while Product.objects.filter(sku=sku).exists():
                sku = _generate_sku(obj.name, category_name)
            obj.sku = sku
        super().save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('body',)
    readonly_fields = ('product', 'user', 'rating', 'created_at')


@admin.register(WishlistItem)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
