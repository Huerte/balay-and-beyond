<div align="center">
  <img src="docs/home.png" alt="Balay & Beyond Banner" width="100%" />
  
  [![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
  [![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://djangoproject.com)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

<div align="center">

**A premium Django e-commerce platform engineered for curated home essentials and modern living spaces.**

[Bug Report](https://github.com/Huerte/BalayAndBeyond/issues) | [Feature Request](https://github.com/Huerte/BalayAndBeyond/issues)

</div>

## Table of Contents
1. [Features](#features)
2. [Visual Tour](#visual-tour)
3. [Installation](#installation)
4. [Deployment (Render)](#deployment-render)
5. [Architecture](#architecture)
6. [Contributing](#contributing)
7. [License](#license)

## Features

* **Dynamic Filter System** 
  Server-side state management for category, price, and stock filtering using URL query parameters.
* **Intelligent Cart Architecture**
  Asynchronous cart operations with real-time DOM updates via optimized Fetch API calls.
* **Bento-Grid Dashboard**
  A customized `django-jazzmin` administration panel featuring dark mode and strict bento grid layouts.
* **Auto-Generating SKUs**
  Deterministic, collision-resistant SKU generation locked upon product creation.
* **Conditional Checkout Flows**
  Dynamic payment method validation prioritizing Cash on Delivery and structured card inputs.
* **Responsive Visuals**
  Full-screen image lightboxes and fluid grid scaling across all breakpoints.

## Visual Tour

### Home & Catalog
<img src="docs/home.png" alt="Home Page" width="800" />
<img src="docs/shop.png" alt="Shop Catalog" width="800" />

### Product Details & Interaction
<img src="docs/product_view.png" alt="Product View" width="800" />
<img src="docs/wishlist.png" alt="Wishlist Management" width="800" />

### Shopping Cart
<img src="docs/cart.png" alt="Shopping Cart" width="800" />

## Installation

### Prerequisites
* Python 3.10 or higher
* PostgreSQL (for production) or SQLite (for local development)

### Quick Setup

1. Clone the repository
```bash
git clone https://github.com/Huerte/BalayAndBeyond.git
cd BalayAndBeyond
```

2. Set up the virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r src/requirements.txt
```

3. Configure environment variables
```bash
cp src/.env.example src/.env
# Edit src/.env with your local credentials
```

4. Initialize the database
```bash
cd src
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server
```bash
python manage.py runserver
```

## Deployment (Render)

This project is optimized for deployment on Render. The `prod.py` settings file automatically configures WhiteNoise for static file serving and parses database URLs.

### Critical Render Settings

When deploying on the free tier, set the following environment variables in your Render dashboard:

* `DJANGO_SETTINGS_MODULE`: `config.settings.prod`
* `SECRET_KEY`: A secure random string
* `ALLOWED_HOSTS`: `.onrender.com`
* `DATABASE_URL`: Your PostgreSQL internal database URL

Note regarding media files on free tiers: Render's free instances use ephemeral file systems. Any user-uploaded images (profile pictures, new product photos) will disappear when the server restarts. You must configure an external storage bucket like AWS S3 or Cloudinary for persistent media storage in production.

## Architecture

* **Django ORM** handles all data relationships, enforcing strict protections on category deletion.
* **Vanilla JavaScript** drives the cart and wishlist toggles to keep the client bundle size minimal.
* **Tailwind CSS** manages the visual system via a curated design token palette (`primary`, `surface`, `text`, `muted`).
* **WhiteNoise** intercepts static file requests at the WSGI layer for zero-dependency asset serving.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-logic`)
3. Commit your changes (`git commit -m 'Add new logic'`)
4. Push to the branch (`git push origin feature/new-logic`)
5. Open a Pull Request

## Credits

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/Huerte">
          <img src="https://github.com/Huerte.png" width="100px;" alt="Huerte"/>
          <br />
          <b>Huerte</b>
        </a>
      </td>
    </tr>
  </table>
</div>

## License

This project is licensed under the MIT License. See the LICENSE file for details.
