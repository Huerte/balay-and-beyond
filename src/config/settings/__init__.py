import os
from dotenv import load_dotenv

load_dotenv()

django_env = os.environ.get("DJANGO_ENV", "development").lower()

if django_env == "production":
    from .prod import *
else:
    from .dev import *
