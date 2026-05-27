from django.urls import path
from . import views


app_name = 'store'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('shop/category/<slug:slug>/', views.CategoryRedirectView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/review/', views.SubmitReviewView.as_view(), name='submit_review'),

    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('shipping-returns/', views.ShippingReturnsView.as_view(), name='shipping'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('care-guide/', views.CareGuideView.as_view(), name='care_guide'),
    path('privacy-policy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms-of-service/', views.TermsView.as_view(), name='terms'),

    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('api/wishlist/toggle/', views.ToggleWishlistView.as_view(), name='wishlist_toggle'),
]
