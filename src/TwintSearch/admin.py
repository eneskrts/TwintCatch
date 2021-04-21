from django.contrib import admin
from .models import Task,ScheduledTask,ScheduledTaskInstance


class TaskAdmin(admin.ModelAdmin):
    list_display = ['keyword','user','created_on']
    list_display_links = ['keyword','user']
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ['keyword','user','created_on']

# Register your models here.
admin.site.register(Task,TaskAdmin)
admin.site.register(ScheduledTask,ScheduledTaskAdmin)
admin.site.register(ScheduledTaskInstance)
