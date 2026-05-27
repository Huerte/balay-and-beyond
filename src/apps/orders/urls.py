from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/remove/', views.RemoveFromCartView.as_view(), name='cart_remove'),
    path('cart/update/', views.UpdateCartView.as_view(), name='cart_update'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('history/', views.OrderHistoryView.as_view(), name='history'),
    path('<int:order_id>/', views.OrderConfirmationView.as_view(), name='confirmation'),
]
