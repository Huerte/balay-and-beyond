from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address
import random


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        base_username = user.email.split('@')[0]
        username = base_username
        if User.objects.filter(username=username).exists():
            username = f"{base_username}{random.randint(1000, 9999)}"
        user.username = username
        if commit:
            user.save()
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('label', 'street', 'city', 'province', 'zip_code', 'country', 'is_default')
        widgets = {
            'label': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'street': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'province': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'zip_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary bg-surface border-muted/30 rounded focus:ring-primary focus:ring-offset-0 cursor-pointer'}),
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-muted/30 rounded bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-sm transition-colors'}),
        }
