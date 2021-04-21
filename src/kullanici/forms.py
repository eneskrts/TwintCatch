from django.db import models
from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
import json
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.forms import ValidationError
from django.templatetags.static import static
import re,os
from django.contrib.auth.models import User
#from django.core.exceptions import ValidationError
from django.forms import ValidationError





class LoginForm(forms.Form):
    username = forms.CharField(required=True,max_length=40,label="Kullanıcı Adı",
                            widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Kullanıcı Adınızı Giriniz'}))
    password = forms.CharField(required=True,max_length=40,label="Password",
                            widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Şifrenizi Giriniz'}))

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        user = None
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
        if not user :
            raise forms.ValidationError("Bu Bilgilerde kullanıcı bulunamadı")

        kullanici = authenticate(username=user.username,password=password)



        if not kullanici :
            raise forms.ValidationError("Bu Bilgilerde kullanıcı bulunamadı")
