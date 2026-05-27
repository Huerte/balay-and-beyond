from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('address/add/', views.AddAddressView.as_view(), name='address_add'),
    path('address/<int:pk>/delete/', views.DeleteAddressView.as_view(), name='address_delete'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url=reverse_lazy('accounts:dashboard')
    ), name='password_change'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot-password/success/', views.ForgotPasswordSuccessView.as_view(), name='forgot_password_success'),
]
