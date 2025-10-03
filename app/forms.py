# accounts/forms.py
from django import forms

class LoginForm(forms.Form):
    dni = forms.CharField(label="DNI", max_length=15)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
