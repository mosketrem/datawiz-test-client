from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=200, label='Email', help_text='Required', required=True)
    password = forms.CharField(label='Password', help_text='Required', widget=forms.PasswordInput, required=True)
