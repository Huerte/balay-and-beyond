import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.store.models import Category

User = get_user_model()

# Maps category slug -> source image filename under static/assets/categories/
CATEGORY_IMAGES: dict[str, str] = {
    'kitchen':          'kitchen.jpg',
    'living-room':      'living-room.webp',
    'bedroom':          'bedroom.jpg',
    'bathroom':         'bathroom.jpg',
    'cleaning-laundry': 'laundry.jpg',
    'outdoor-garden':   'gardening.webp',
}

ROOT_CATEGORIES = [
    {'name': 'Kitchen',            'slug': 'kitchen'},
    {'name': 'Living Room',        'slug': 'living-room'},
    {'name': 'Bedroom',            'slug': 'bedroom'},
    {'name': 'Bathroom',           'slug': 'bathroom'},
    {'name': 'Cleaning & Laundry', 'slug': 'cleaning-laundry'},
    {'name': 'Outdoor & Garden',   'slug': 'outdoor-garden'},
]

# Source directory for category images (inside the project's static folder)
STATIC_CATEGORIES_DIR = Path(settings.BASE_DIR) / 'static' / 'assets' / 'categories'

# Destination inside MEDIA_ROOT (matches ImageField upload_to='categories/')
MEDIA_CATEGORIES_DIR = Path(settings.MEDIA_ROOT) / 'categories'


def _copy_category_image(slug: str) -> str | None:
    """
    Copy the image for a given slug from static → media/categories/.
    Returns the relative path stored in the ImageField, or None if the
    source file is missing.
    """
    filename = CATEGORY_IMAGES.get(slug)
    if not filename:
        return None

    src = STATIC_CATEGORIES_DIR / filename
    if not src.exists():
        return None

    MEDIA_CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)
    dst = MEDIA_CATEGORIES_DIR / filename
    shutil.copy2(src, dst)

    # ImageField stores paths relative to MEDIA_ROOT
    return f'categories/{filename}'


class Command(BaseCommand):
    help = 'Seeds the database with demo accounts and categories (no products or orders).'

    def handle(self, *args, **options):
        self.stdout.write('=== Balay & Beyond init starting ===')

        # --- Demo accounts ---
        admin_account, created = User.objects.get_or_create(
            email='admin@gmail.com',
            defaults={
                'username':     'admin_demo',
                'first_name':   'Admin',
                'last_name':    'User',
                'is_staff':     True,
                'is_superuser': True,
            }
        )
        if created:
            admin_account.set_password('admin1234')
            admin_account.save()
            self.stdout.write('  Created admin account.')
        else:
            self.stdout.write('  Admin account already exists.')

        regular_account, created = User.objects.get_or_create(
            email='user@gmail.com',
            defaults={
                'username':   'user_demo',
                'first_name': 'Regular',
                'last_name':  'User',
            }
        )
        if created:
            regular_account.set_password('user1234')
            regular_account.save()
            self.stdout.write('  Created regular account.')
        else:
            self.stdout.write('  Regular account already exists.')

        # --- Seed categories ---
        for i, cat_data in enumerate(ROOT_CATEGORIES):
            image_path = _copy_category_image(cat_data['slug'])

            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name':       cat_data['name'],
                    'sort_order': i + 1,
                    'image':      image_path or '',
                }
            )

            if created:
                label = 'with image' if image_path else 'NO image found'
                self.stdout.write(f"  Created category: {cat.name} ({label})")
            else:
                # Update image if not already set
                if image_path and not cat.image:
                    cat.image = image_path
                    cat.save(update_fields=['image'])
                    self.stdout.write(f"  Updated image for existing category: {cat.name}")
                else:
                    self.stdout.write(f"  Category already exists: {cat.name}")

        self.stdout.write(self.style.SUCCESS('=== Init complete ==='))

