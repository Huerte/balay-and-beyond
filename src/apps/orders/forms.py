from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    street = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    province = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)
    shipping_method = forms.CharField(max_length=50)
