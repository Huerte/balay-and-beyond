#!/usr/bin/env bash
# Make this file executable before pushing: chmod +x build.sh

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input --settings=config.settings.prod

# Apply database migrations
python manage.py migrate --settings=config.settings.prod

# Seed demo data (safe for re-runs via get_or_create)
python manage.py seed_demo --settings=config.settings.prod
