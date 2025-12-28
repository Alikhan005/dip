from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import ProfileForm, SignupForm


class LoginGateView(BaseLoginView):
    """Login screen with a minimal layout."""

    extra_context = {"hide_nav": True}


class LogoutAllowGetView(LogoutView):
    """Allow logout via GET for UX parity with legacy behavior."""

    http_method_names = ["get", "head", "options", "post"]


class SignupView(CreateView):
    model = get_user_model()
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")
    extra_context = {"hide_nav": True}

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error("username", "User with this username already exists.")
            return self.form_invalid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileForm
    template_name = "registration/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user
