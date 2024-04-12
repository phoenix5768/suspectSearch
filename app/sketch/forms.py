# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('iin', 'first_name', 'last_name', 'dob', 'department', 'badge_number', 'role')


class CustomUserCreationForm(UserCreationForm):
    model = CustomUser
    plaintext_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    fields = ('iin', 'first_name', 'last_name', 'dob', 'department', 'badge_number', 'role')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('plaintext_password',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["plaintext_password"]:
            # This is where you handle the plaintext password for demonstration purposes
            # For example, temporarily storing it to show in the admin interface or logging it securely
            # Ensure this is done securely and is compliant with your security policy
            pass
        if commit:
            user.save()
        return user