from django.shortcuts import get_object_or_404
from .models import Product, Category


def get_published_products():
    return Product.objects.filter(is_published=True).select_related('category').prefetch_related('images')


def get_category_by_slug(slug):
    return get_object_or_404(Category, slug=slug)


def get_products_by_category(category):
    return Product.objects.filter(category=category, is_published=True).select_related('category').prefetch_related('images')


def get_product_by_slug(slug):
    return get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'variants', 'reviews__user'),
        slug=slug,
        is_published=True
    )


def get_featured_products(limit=4):
    return Product.objects.filter(is_published=True).select_related('category').prefetch_related('images')[:limit]


def get_root_categories():
    return Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
