from django import forms
from .models import *



class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ['name', 'state', 'city', 'pincode', 'address', 'email', 'number', 'specializations']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clinic Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'clinic@example.com'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91xxxxxxxxxx'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = '__all__'