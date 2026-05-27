from django.db.models import QuerySet
from .models import User

def get_user_orders(user: User) -> QuerySet:
    return user.orders.all().order_by('-created_at')

def get_user_addresses(user: User) -> QuerySet:
    return user.addresses.all()
