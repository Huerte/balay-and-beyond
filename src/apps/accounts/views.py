from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.views.generic import CreateView, TemplateView, View, UpdateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User, Address
from .forms import CustomUserCreationForm, AddressForm, UserEditForm
from . import services


class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class LogoutView(AuthLogoutView):
    next_page = 'store:home'


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('store:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = services.get_user_orders(self.request.user)
        context['addresses'] = services.get_user_addresses(self.request.user)
        return context


class AddAddressView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'accounts/address_form.html', {'form': form})
        
    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                request.user.addresses.update(is_default=False)
            address.save()
            return redirect('accounts:dashboard')
        return render(request, 'accounts/address_form.html', {'form': form})


class DeleteAddressView(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.delete()
        return redirect('accounts:dashboard')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:dashboard')

    def get_object(self, queryset=None):
        return self.request.user


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'accounts/forgot_password.html')
        
    def post(self, request):
        # Mockup: just redirect to the success page
        return redirect('accounts:forgot_password_success')


class ForgotPasswordSuccessView(TemplateView):
    template_name = 'accounts/forgot_password_success.html'
