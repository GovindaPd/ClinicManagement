from django import forms
from .models import *

#ckeditor form example
from django_ckeditor_5.widgets import CKEditor5Widget

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


#ckeditor form example
class CkForm(forms.ModelForm):
    """Form for comments to the article."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].required = False

    class Meta:
        model = CkModel
        fields = ("author", "text")
        widgets = {
            "text": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="comment"
            )
        }