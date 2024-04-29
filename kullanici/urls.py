from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from .views import LoginView,LogoutView,AlertView
from django.conf.urls.static import static

urlpatterns = [
    path('login', LoginView, name="login"),
    path('logout', LogoutView, name="logout"),
    path('alerts', AlertView, name='alerts')
]