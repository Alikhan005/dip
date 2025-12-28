from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "faculty",
            "department",
            "password1",
            "password2",
        )
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "role": "Роль в системе",
            "faculty": "Факультет",
            "department": "Кафедра",
        }
        help_texts = {
            "role": "Выберите роль для демонстрации работы системы.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_role_values = {
            User.Role.TEACHER,
            User.Role.DEAN,
            User.Role.UMU,
        }
        allowed_roles = [choice for choice in User.Role.choices if choice[0] in allowed_role_values]
        self.fields["role"].choices = allowed_roles

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            return username
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("User with this username already exists.")
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "faculty", "department")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
            "faculty": "Факультет",
            "department": "Кафедра",
        }
