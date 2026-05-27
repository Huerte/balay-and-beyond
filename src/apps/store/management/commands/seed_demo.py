import json
import random
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.store.models import Category, Product, ProductImage
from apps.orders.models import Order, OrderItem

User = get_user_model()


def _load_json(filepath: str) -> dict | None:
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {filepath}: {exc}") from exc


def _safe_decimal(value, fallback: Decimal = Decimal('0.00')) -> Decimal:
    if value is None:
        return fallback
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return fallback


def _unique_slug(base_slug: str, sku: str) -> str:
    # Derive slug purely from the SKU — guaranteed unique because SKU is unique.
    # e.g. "LVR-40355409" -> "lvr-40355409"
    return slugify(sku)


class Command(BaseCommand):
    help = 'Seeds the database from ikea_store.json and ikea_search_products.json'

    def handle(self, *args, **options):
        self.stdout.write('=== Balay & Beyond seed starting ===')

        # --- Load source files ---
        store_data = _load_json('ikea_store.json')
        search_data = _load_json('ikea_search_products.json')

        if store_data is None and search_data is None:
            self.stdout.write(self.style.ERROR(
                'Neither ikea_store.json nor ikea_search_products.json found in project root.'
            ))
            return

        # --- Demo accounts ---
        admin_account, created = User.objects.get_or_create(
            email='admin@gmail.com',
            defaults={
                'username': 'admin_demo',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_account.set_password('admin1234')
            admin_account.save()
            self.stdout.write('Created admin account.')

        regular_account, created = User.objects.get_or_create(
            email='user@gmail.com',
            defaults={
                'username': 'user_demo',
                'first_name': 'Regular',
                'last_name': 'User',
            }
        )
        if created:
            regular_account.set_password('user1234')
            regular_account.save()
            self.stdout.write('Created regular account.')

        # --- Seed categories from ikea_store.json ---
        # Build a slug -> Category lookup so products can resolve their parent category fast.
        category_by_slug: dict[str, Category] = {}

        if store_data:
            for cat_data in store_data.get('categories', []):
                parent_cat, _ = Category.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults={
                        'name': cat_data['name'],
                        'sort_order': cat_data.get('sort_order', 0),
                        # image is an ImageField — URL strings cannot be stored here directly.
                        # Category images must be uploaded via the admin panel separately.
                    }
                )
                category_by_slug[parent_cat.slug] = parent_cat

                for sub_data in cat_data.get('subcategories', []):
                    child_cat, _ = Category.objects.get_or_create(
                        slug=sub_data['slug'],
                        defaults={
                            'name': sub_data['name'],
                            'parent': parent_cat,
                            'sort_order': sub_data.get('sort_order', 0),
                        }
                    )
                    category_by_slug[child_cat.slug] = child_cat

            self.stdout.write(f'Resolved {len(category_by_slug)} categories.')

        # If we only have search data (no store file), populate category_by_slug from DB.
        if not category_by_slug:
            for cat in Category.objects.filter(parent__isnull=True):
                category_by_slug[cat.slug] = cat

        # --- Merge products from both files ---
        all_products: list[dict] = []

        if store_data:
            all_products.extend(store_data.get('products', []))

        if search_data:
            all_products.extend(search_data.get('products', []))

        self.stdout.write(f'Processing {len(all_products)} products...')

        created_products: list[Product] = []
        skipped = 0

        for item in all_products:
            sku = item.get('sku', '').strip()
            name = item.get('name', '').strip()

            if not sku or not name:
                skipped += 1
                continue

            # Resolve category: products carry a category_slug field.
            cat_slug = item.get('category_slug', '')
            resolved_category = category_by_slug.get(cat_slug)

            if resolved_category is None:
                # Last resort: create a bare parent category so nothing crashes.
                if cat_slug:
                    resolved_category, _ = Category.objects.get_or_create(
                        slug=cat_slug,
                        defaults={'name': cat_slug.replace('-', ' ').title()}
                    )
                    category_by_slug[cat_slug] = resolved_category
                else:
                    skipped += 1
                    continue

            # Prices are already in PHP — no conversion.
            price_php = _safe_decimal(item.get('price'), Decimal('0.00'))
            compare_price_php = _safe_decimal(item.get('compare_price'))
            # compare_price of 0 is meaningless — treat as absent.
            compare_price_php = compare_price_php if compare_price_php > Decimal('0') else None

            # Null stock -> 0 (PositiveIntegerField default).
            stock = item.get('stock')
            stock_int = int(stock) if stock is not None else 0

            # Slug must be globally unique. Use SKU suffix to break ties.
            base_slug = item.get('slug') or slugify(name)
            unique_product_slug = _unique_slug(base_slug, sku)

            product_instance, product_created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'slug': unique_product_slug,
                    'description': item.get('description', ''),
                    'category': resolved_category,
                    'price': price_php,
                    'compare_price': compare_price_php,
                    'stock': stock_int,
                    'is_published': item.get('is_published', True),
                }
            )
            created_products.append(product_instance)

            if product_created:
                # images list is empty in both JSONs; skip ProductImage creation to avoid null URLs.
                # When real image URLs are available, add them here via ProductImage.objects.create().
                image_list = item.get('images', [])
                for idx, img_url in enumerate(image_list):
                    if img_url:
                        ProductImage.objects.create(
                            product=product_instance,
                            url=img_url,
                            alt=name,
                            sort_order=idx,
                        )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(created_products)} products ({skipped} skipped due to missing SKU/category).'
        ))

        # --- Demo orders ---
        order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

        # Need at least 3 products to sample from for order creation.
        if len(created_products) < 3:
            self.stdout.write(self.style.WARNING('Not enough products for demo orders. Skipping.'))
        elif Order.objects.filter(user=regular_account).count() < 5:
            for status_label in order_statuses:
                sample_size = min(random.randint(2, 3), len(created_products))
                selected_products = random.sample(created_products, sample_size)

                order_instance = Order.objects.create(
                    user=regular_account,
                    status=status_label,
                    total=Decimal('0.00'),
                    shipping_address={
                        'full_name': 'Regular User',
                        'street': '456 Sample Blvd.',
                        'city': 'Quezon City',
                        'province': 'Metro Manila',
                        'zip_code': '1100',
                        'country': 'Philippines',
                    },
                    shipping_method='Standard',
                    shipping_cost=Decimal('0.00'),
                )

                running_total = Decimal('0.00')
                for prod in selected_products:
                    purchase_qty = random.randint(1, 2)
                    line_price = prod.price * purchase_qty
                    OrderItem.objects.create(
                        order=order_instance,
                        product=prod,
                        quantity=purchase_qty,
                        unit_price=prod.price,
                        line_total=line_price,
                    )
                    running_total += line_price

                order_instance.total = running_total
                order_instance.save()

            self.stdout.write(self.style.SUCCESS(f'Created {len(order_statuses)} demo orders.'))

        self.stdout.write(self.style.SUCCESS('=== Seed complete ==='))

