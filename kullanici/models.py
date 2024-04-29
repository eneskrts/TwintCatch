from django.db import models

# Create your models here.
from TwintSearch.models import ScheduledTask
from django.contrib.auth.models import User


class UserAlert(models.Model):
    class Meta:
        verbose_name_plural = "Kullanıcı Bildirimleri"
        
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    task = models.ForeignKey(ScheduledTask,on_delete=models.CASCADE)
    seen = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return self.user.username + self.task.keyword
