from django import forms
from .models import *


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = '__all__'