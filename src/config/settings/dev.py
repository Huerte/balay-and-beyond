from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

try:
    import django_extensions
    if 'django_extensions' not in INSTALLED_APPS:
        INSTALLED_APPS = INSTALLED_APPS + ['django_extensions']
except ImportError:
    pass
