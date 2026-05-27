from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.ProcessPaymentView.as_view(), name='process'),
]
