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
        login(self.request, self.object, backend='apps.accounts.backends.EmailBackend')
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        from apps.orders.models import Order
        from django.db.models import Case, When, Value, IntegerField

        context = super().get_context_data(**kwargs)
        
        # Priority tiers:
        # 0 — unread update on any order (temporary override)
        # 1 — new orders: pending, confirmed
        # 2 — in-progress: processing, shipped
        # 3 — recently delivered
        # 4 — cancelled / everything else
        # Within each tier, most recently updated appears first.
        orders = services.get_user_orders(self.request.user).annotate(
            priority=Case(
                When(has_unread_update=True, then=Value(0)),
                When(status__in=['pending', 'confirmed'], then=Value(1)),
                When(status__in=['processing', 'shipped'], then=Value(2)),
                When(status='delivered', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('priority', '-updated_at')
        
        context['orders'] = orders[:2]
        context['addresses'] = services.get_user_addresses(self.request.user)

        # Snapshot all unread order IDs to drive both the highlights and the "View All" dot.
        # Do NOT clear flags here — the History page is responsible for clearing once the
        # user has actually seen every highlighted container.
        all_updated_ids = list(
            Order.objects.filter(user=self.request.user, has_unread_update=True)
            .values_list('id', flat=True)
        )
        shown_order_ids = [o.id for o in orders[:2]]
        extra_update_count = len([uid for uid in all_updated_ids if uid not in shown_order_ids])

        context['updated_order_ids'] = all_updated_ids
        context['extra_update_count'] = extra_update_count

        # Only dismiss the nav dot when every update fits inside the visible 2 slots
        if extra_update_count == 0 and self.request.user.has_unread_orders:
            self.request.user.has_unread_orders = False
            self.request.user.save(update_fields=['has_unread_orders'])

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
