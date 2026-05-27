"""
seed_products.py
----------------
Populates the database with Filipino household products grouped by the
store's existing categories. All image URLs point to Unsplash (free,
no-auth required). For educational / demo purposes only.

Run:
    python manage.py seed_products
    python manage.py seed_products --wipe   # clears existing products first
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.store.models import Category, Product, ProductImage

# ---------------------------------------------------------------------------
# PRODUCT DATA
# Each entry: name, description, price (PHP), compare_price (PHP, optional),
#             stock, category_slug, images (list of Unsplash URLs)
# ---------------------------------------------------------------------------
PRODUCTS = [
    # ── KITCHEN ────────────────────────────────────────────────────────────
    {
        "name": "Earthen Stoneware Rice Bowl Set",
        "description": "A set of four hand-thrown stoneware rice bowls with a natural matte glaze. Microwave and dishwasher safe. Each bowl holds approximately 350ml — the right size for a Filipino cup of rice.",
        "price": "599.00",
        "compare_price": "799.00",
        "stock": 45,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1610701596061-2ecf227e85b2?w=800&q=80",
            "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=800&q=80",
        ],
    },
    {
        "name": "Acacia Wood Chopping Board",
        "description": "Solid acacia cutting board with juice groove along the perimeter. Naturally antimicrobial and gentle on knife edges. Wipe clean and oil occasionally with food-grade mineral oil to maintain its warm grain.",
        "price": "749.00",
        "compare_price": "950.00",
        "stock": 30,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
            "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=800&q=80",
        ],
    },
    {
        "name": "Ceramic Pour-Over Coffee Set",
        "description": "A minimal ceramic pour-over dripper and matching mug. Made from high-fire stoneware, it retains heat well during your morning brew. Compatible with standard #2 cone filters.",
        "price": "890.00",
        "compare_price": None,
        "stock": 20,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80",
            "https://images.unsplash.com/photo-1509785307050-d4066910ec1e?w=800&q=80",
        ],
    },
    {
        "name": "Handwoven Rattan Fruit Basket",
        "description": "Traditional Filipino-style rattan weave basket for storing fruits, vegetables, or bread on the countertop. Keeps produce ventilated and looking good. Approximately 30cm diameter.",
        "price": "420.00",
        "compare_price": "550.00",
        "stock": 60,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=800&q=80",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        ],
    },
    {
        "name": "Terracotta Pitcher with Lid",
        "description": "A classic Filipino palayok-inspired pitcher perfect for water, calamansi juice, or salabat (ginger tea). The unglazed terracotta naturally cools liquids and adds earthy character to any dining table.",
        "price": "550.00",
        "compare_price": None,
        "stock": 25,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
        ],
    },
    {
        "name": "Stainless Steel Kaldero Set (3-piece)",
        "description": "The Filipino kitchen staple. A three-piece kaldero set in 18/10 stainless steel — 20cm, 24cm, and 28cm — with sturdy riveted handles and tight-fitting lids. Built for adobo, sinigang, and everything in between.",
        "price": "1250.00",
        "compare_price": "1600.00",
        "stock": 35,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=800&q=80",
            "https://images.unsplash.com/photo-1585515656973-f22ce00f5d9e?w=800&q=80",
        ],
    },
    {
        "name": "Bamboo Steamer Basket Set",
        "description": "Two-tier bamboo steamer for siomai, puto, or leafy vegetables. Natural bamboo construction that imparts no chemical taste. Fits standard 28cm woks and pots.",
        "price": "380.00",
        "compare_price": "480.00",
        "stock": 40,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1563379091339-03246963d651?w=800&q=80",
            "https://images.unsplash.com/photo-1547592180-85f173990554?w=800&q=80",
        ],
    },
    {
        "name": "Hand-painted Salad Bowl",
        "description": "A large 30cm ceramic salad bowl with hand-painted floral motifs. Great for ensalada, fruit salad, or serving rice at family gatherings. Each piece is unique due to the hand-applied glaze.",
        "price": "680.00",
        "compare_price": None,
        "stock": 18,
        "category_slug": "kitchen",
        "images": [
            "https://images.unsplash.com/photo-1610701596061-2ecf227e85b2?w=800&q=80",
        ],
    },

    # ── LIVING ROOM ─────────────────────────────────────────────────────────
    {
        "name": "Banig-Weave Floor Cushion",
        "description": "Oversized floor cushion upholstered in banig-inspired woven fabric with kapok filling. Perfect for casual sala seating, kids' nooks, or as additional seating during gatherings. 60cm × 60cm.",
        "price": "950.00",
        "compare_price": "1200.00",
        "stock": 22,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80",
        ],
    },
    {
        "name": "Rattan Accent Side Table",
        "description": "A slim, lightweight rattan side table that works as a bedside table or sala accent. The open-weave shelf below fits paperbacks, remotes, and magazines. Holds up to 15kg.",
        "price": "1450.00",
        "compare_price": "1800.00",
        "stock": 15,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
            "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800&q=80",
        ],
    },
    {
        "name": "Woven Abaca Table Runner",
        "description": "A 180cm table runner hand-woven from natural abaca fiber — a plant native to the Philippines. Adds texture and warmth to dining tables without overpowering the setting.",
        "price": "320.00",
        "compare_price": None,
        "stock": 55,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1567016432779-094069958ea5?w=800&q=80",
        ],
    },
    {
        "name": "Hand-poured Lemongrass Soy Candle",
        "description": "A 250ml glass vessel soy candle scented with real lemongrass essential oil — a fragrance familiar in every Filipino home. 45-hour burn time. Wicks are 100% cotton.",
        "price": "350.00",
        "compare_price": "420.00",
        "stock": 80,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1602028915047-37269d1a73f7?w=800&q=80",
            "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=800&q=80",
        ],
    },
    {
        "name": "Seagrass Storage Basket (Large)",
        "description": "A large 35cm seagrass storage basket with cotton rope handles. Perfect for storing extra blankets, kids' toys, or laundry in the sala. Naturally odor-resistant.",
        "price": "780.00",
        "compare_price": "980.00",
        "stock": 28,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
            "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800&q=80",
        ],
    },
    {
        "name": "Ceramic Table Lamp with Linen Shade",
        "description": "A matte clay-body table lamp with a natural linen shade. The warm bulb glow through the shade creates soft, ambient light ideal for living rooms and bedrooms. Shade diameter: 28cm. Cord length: 1.5m.",
        "price": "1890.00",
        "compare_price": "2400.00",
        "stock": 12,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80",
            "https://images.unsplash.com/photo-1513506003901-1e6a35fb6d0d?w=800&q=80",
        ],
    },
    {
        "name": "Minimalist Wooden Wall Clock",
        "description": "A 30cm wall clock with a solid ash wood frame and clean, numberless face. Runs on a single AA battery with a silent quartz movement — no ticking to disturb quiet spaces.",
        "price": "650.00",
        "compare_price": None,
        "stock": 33,
        "category_slug": "living-room",
        "images": [
            "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=800&q=80",
        ],
    },

    # ── BEDROOM ─────────────────────────────────────────────────────────────
    {
        "name": "Washed Cotton Duvet Cover Set",
        "description": "A queen-size duvet cover with two matching pillowcases in pre-washed 100% cotton. The garment-wash process gives it a relaxed, lived-in softness from day one. Available in natural white and warm beige.",
        "price": "1650.00",
        "compare_price": "2100.00",
        "stock": 25,
        "category_slug": "bedroom",
        "images": [
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80",
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
        ],
    },
    {
        "name": "Kapok-filled Body Pillow",
        "description": "A long 50cm × 100cm body pillow filled with sustainably harvested kapok — the same plant-based fiber Filipino families have used for generations. Naturally hypoallergenic and breathable for the Philippine climate.",
        "price": "890.00",
        "compare_price": "1100.00",
        "stock": 40,
        "category_slug": "bedroom",
        "images": [
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80",
        ],
    },
    {
        "name": "Bamboo Bedside Organizer",
        "description": "A slim bamboo shelf that sits on your nightstand and neatly holds a glass of water, a phone, and a book. The slanted phone slot works with most cases and propped-up tablets.",
        "price": "420.00",
        "compare_price": None,
        "stock": 50,
        "category_slug": "bedroom",
        "images": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
        ],
    },
    {
        "name": "Chunky Knit Cotton Throw",
        "description": "A 130cm × 170cm hand-knitted throw blanket in 100% natural cotton. The open-knit weave keeps it light enough for Philippine evenings while adding texture to any bed or sofa.",
        "price": "1200.00",
        "compare_price": "1500.00",
        "stock": 20,
        "category_slug": "bedroom",
        "images": [
            "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=800&q=80",
            "https://images.unsplash.com/photo-1567016432779-094069958ea5?w=800&q=80",
        ],
    },
    {
        "name": "Rattan Wardrobe Organizer Set",
        "description": "A set of six rattan-front drawer inserts that slot into standard wardrobe shelves. Keeps folded clothes, accessories, and small items separated and visible without needing a dedicated chest of drawers.",
        "price": "990.00",
        "compare_price": "1250.00",
        "stock": 18,
        "category_slug": "bedroom",
        "images": [
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        ],
    },

    # ── BATHROOM ────────────────────────────────────────────────────────────
    {
        "name": "Organic Cotton Bath Towel Set",
        "description": "A set of two 70cm × 140cm bath towels woven from GOTS-certified organic cotton. Dense 600 GSM weave is absorbent and dries quickly in the Philippine humidity. Wash before first use for maximum softness.",
        "price": "1100.00",
        "compare_price": "1400.00",
        "stock": 35,
        "category_slug": "bathroom",
        "images": [
            "https://images.unsplash.com/photo-1505691723518-36a5ac3be353?w=800&q=80",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        ],
    },
    {
        "name": "Bamboo Bathroom Shelf",
        "description": "A three-tier freestanding bamboo shelf sized to fit over standard Filipino toilet tanks (fits tanks up to 35cm wide). Stores extra rolls, soaps, and small toiletries while keeping them off the floor.",
        "price": "850.00",
        "compare_price": "1100.00",
        "stock": 22,
        "category_slug": "bathroom",
        "images": [
            "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=800&q=80",
        ],
    },
    {
        "name": "Stone Resin Soap Dish",
        "description": "A heavy stone-resin soap dish with a ridged surface that drains water away from your bar soap, extending its life. Works with standard bar soaps and glycerin soaps popular in Filipino skincare routines.",
        "price": "280.00",
        "compare_price": None,
        "stock": 70,
        "category_slug": "bathroom",
        "images": [
            "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&q=80",
        ],
    },
    {
        "name": "Cotton Waffle Hand Towel Set (3-piece)",
        "description": "Three 40cm × 70cm hand towels in a waffle-weave cotton that is lighter than terry cloth and dries faster — ideal for bathrooms without air conditioning. Pre-washed for immediate softness.",
        "price": "480.00",
        "compare_price": "600.00",
        "stock": 55,
        "category_slug": "bathroom",
        "images": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
        ],
    },
    {
        "name": "Amber Glass Refillable Dispenser Set",
        "description": "A set of three 300ml amber glass pump dispensers for shampoo, conditioner, and body wash. The amber glass blocks UV light to preserve product quality. Laser-etched labels are water-resistant.",
        "price": "650.00",
        "compare_price": "820.00",
        "stock": 30,
        "category_slug": "bathroom",
        "images": [
            "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&q=80",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
        ],
    },

    # ── CLEANING & LAUNDRY ──────────────────────────────────────────────────
    {
        "name": "Beechwood Scrub Brush Set",
        "description": "A set of three beechwood scrub brushes — one large pot scrubber, one tile brush, and one bottle brush — with stiff natural-fiber bristles. The long handles keep hands away from harsh cleaning solutions.",
        "price": "390.00",
        "compare_price": "490.00",
        "stock": 45,
        "category_slug": "cleaning-laundry",
        "images": [
            "https://images.unsplash.com/photo-1563453392212-326f5e854473?w=800&q=80",
        ],
    },
    {
        "name": "Heavy-duty Canvas Laundry Bag",
        "description": "A 50-liter waxed canvas laundry bag with a drawstring top and reinforced handles. The wax-coated exterior repels the moisture typical of wet laundry trips to the poso or washing machine.",
        "price": "450.00",
        "compare_price": None,
        "stock": 38,
        "category_slug": "cleaning-laundry",
        "images": [
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        ],
    },
    {
        "name": "Natural Fiber Doormat (60cm × 90cm)",
        "description": "A coir doormat woven from coconut husk fiber. Tough enough to scrub the mud and dust off shoes before entering the house. The open-weave drains rainwater quickly. Fits standard Filipino gate entrances.",
        "price": "520.00",
        "compare_price": "650.00",
        "stock": 50,
        "category_slug": "cleaning-laundry",
        "images": [
            "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80",
        ],
    },
    {
        "name": "Bamboo Clothes Hangers (Set of 20)",
        "description": "Twenty slim bamboo clothes hangers that take up 30% less rod space than plastic hangers. Naturally smooth surface prevents fabric snags. Suitable for shirts, dresses, and light jackets.",
        "price": "350.00",
        "compare_price": "450.00",
        "stock": 65,
        "category_slug": "cleaning-laundry",
        "images": [
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        ],
    },

    # ── OUTDOOR & GARDEN ────────────────────────────────────────────────────
    {
        "name": "Terracotta Planter Trio",
        "description": "Three unglazed terracotta planters in graduated sizes (12cm, 18cm, 25cm diameter). The porous clay wicks away excess moisture and prevents root rot — ideal for the humidity of the Philippine climate. Drainage holes included.",
        "price": "580.00",
        "compare_price": "750.00",
        "stock": 40,
        "category_slug": "outdoor-garden",
        "images": [
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80",
            "https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=800&q=80",
        ],
    },
    {
        "name": "Galvanized Steel Watering Can (2L)",
        "description": "A classic 2-liter galvanized steel watering can with a long spout for reaching plants on balcony racks. Rust-resistant coating suited for outdoor use in humid climates. Great for herbs, succulents, and potted vegetables.",
        "price": "490.00",
        "compare_price": None,
        "stock": 30,
        "category_slug": "outdoor-garden",
        "images": [
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80",
        ],
    },
    {
        "name": "Macrame Plant Hanger (Set of 2)",
        "description": "Two handcrafted macrame plant hangers made from natural cotton rope. Each holds pots up to 20cm in diameter. Hang from ceiling hooks, bahay-kubo eaves, or balcony railings to display trailing plants like pothos or string-of-pearls.",
        "price": "340.00",
        "compare_price": "420.00",
        "stock": 55,
        "category_slug": "outdoor-garden",
        "images": [
            "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=800&q=80",
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80",
        ],
    },
    {
        "name": "Foldable Monoblock-Style Bamboo Chair",
        "description": "A foldable bamboo chair inspired by the ever-present Filipino monoblock, but built from natural whole bamboo. Lightweight at 2.5kg, holds up to 120kg, and stores flat when not in use. Perfect for patios and garden gatherings.",
        "price": "1350.00",
        "compare_price": "1700.00",
        "stock": 20,
        "category_slug": "outdoor-garden",
        "images": [
            "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800&q=80",
        ],
    },
    {
        "name": "Woven Outdoor Lantern (Set of 2)",
        "description": "Two rattan-wrapped lanterns sized for pillar candles (not included). The woven panels cast geometric shadows when lit, perfect for outdoor dining setups during fiestas or evening gatherings.",
        "price": "760.00",
        "compare_price": "960.00",
        "stock": 25,
        "category_slug": "outdoor-garden",
        "images": [
            "https://images.unsplash.com/photo-1513506003901-1e6a35fb6d0d?w=800&q=80",
        ],
    },
]


class Command(BaseCommand):
    help = "Seeds the database with Filipino household products for demo purposes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete all existing products and images before seeding.",
        )

    def handle(self, *args, **options):
        self.stdout.write("=== Balay & Beyond product seed starting ===")

        if options["wipe"]:
            deleted_count, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Wiped {deleted_count} existing products."))

        created = 0
        skipped = 0
        missing_cats = set()

        for idx, data in enumerate(PRODUCTS):
            cat_slug = data["category_slug"]

            try:
                category = Category.objects.get(slug=cat_slug)
            except Category.DoesNotExist:
                missing_cats.add(cat_slug)
                skipped += 1
                continue

            # Build a URL-safe unique slug from the product name + index
            base_slug = slugify(data["name"])
            slug = f"{base_slug}-{idx + 1:03d}"

            # SKU derived from category slug + sequential index
            sku = f"{cat_slug.upper()[:3]}-{(idx + 1):04d}"

            product, was_created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": data["name"],
                    "slug": slug,
                    "description": data["description"],
                    "category": category,
                    "price": Decimal(data["price"]),
                    "compare_price": Decimal(data["compare_price"]) if data.get("compare_price") else None,
                    "stock": data["stock"],
                    "is_published": True,
                },
            )

            if was_created:
                for sort_idx, img_url in enumerate(data.get("images", [])):
                    ProductImage.objects.create(
                        product=product,
                        url=img_url,
                        alt=data["name"],
                        sort_order=sort_idx,
                    )
                created += 1
            else:
                skipped += 1

        if missing_cats:
            self.stdout.write(self.style.WARNING(
                f"Skipped {len(missing_cats)} category slug(s) not found in DB: {', '.join(missing_cats)}\n"
                "Run the existing seed_init / seed_demo commands first to create categories."
            ))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created} products, skipped {skipped} (already exist or missing category)."
        ))
        self.stdout.write("=== Seed complete ===")
