from django import forms
from .models import Policeman, CriminalsData


class CriminalsDataForm(forms.ModelForm):
    class Meta:
        model = CriminalsData
        fields = ['iin', 'first_name', 'last_name', 'dob', 'martial_status', 'offence', 'zip_code', 'picture']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }


class PolicemanForm(forms.ModelForm):
    class Meta:
        model = Policeman
        fields = ['first_name', 'last_name', 'iin', 'dob', 'department', 'badge_number', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
