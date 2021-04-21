from django.contrib import admin
from .models import UserAlert
# Register your models here.
class UserAlertAdmin(admin.ModelAdmin):
    list_display = ['user','task','seen']
    list_filter = ["user","task","seen"]


admin.site.register(UserAlert,UserAlertAdmin)
