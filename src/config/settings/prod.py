import os
from .base import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

_render_url = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if _render_url and _render_url not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_url)

CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host]

from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomWhiteNoiseStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False

    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            if isinstance(processed, Exception):
                # Skip missing source map errors from vendor files
                yield name, None, True
            else:
                yield name, hashed_name, processed

STORAGES["staticfiles"] = {
    "BACKEND": "config.settings.prod.CustomWhiteNoiseStorage",
}

import dj_database_url
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=0,  # 0 for Supabase connection pooler compatibility
            conn_health_checks=True,
            ssl_require=True
        )
    }

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True