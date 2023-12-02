from django import forms
from .models import *


class AddPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Playlist
        fields = ("name", "description", "cover")
        widgets = {
            "name": forms.TextInput(attrs={
                'class': 'input', 'placeholder': "enter playlist name here"}),
            "description": forms.Textarea(
                attrs={'class': 'input', 'cols': 60, 'rows': 2,
                       'placeholder': "enter description here"}),
        }


"""class AddRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ("username", "email", "password")
        widgets = {
            "name": forms.TextInput(attrs={
                'class': 'input', 'placeholder': "enter playlist name here"}),
            "description": forms.PasswordInput(
                attrs={'class': 'input', placeholder': "enter description here"}),
        }"""