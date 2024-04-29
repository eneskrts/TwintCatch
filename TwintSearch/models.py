from django.db import models
from rq.job import Job
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django_rq import get_connection,get_scheduler
from django.contrib.auth.models import User
class Task(models.Model):
    class Meta:
        verbose_name_plural = "Tek Seferlik Görevler"
        verbose_name = "Tek Seferlik Görev"

    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    keyword = models.CharField(max_length=128,unique=True)
    job_id = models.CharField(max_length=128)
    
    result = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.keyword


class ScheduledTask(models.Model):
    class Meta:
        verbose_name_plural = "Sürekli Görevler"
        verbose_name = "Sürekli Görev"

    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    keyword = models.CharField(max_length=128,unique=True)
    job_id = models.CharField(max_length=128)


class ScheduledTaskInstance(models.Model):
    class Meta:
        verbose_name_plural = "Sürekli Görev Instance"
        verbose_name = "Sürekli Görev"

    scheduled_task = models.ForeignKey('ScheduledTask',on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    result = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.scheduled_task.keyword


@receiver(pre_delete, sender=ScheduledTask)
def delete_job(sender, instance, using, **kwargs):

    try:
        job_id = instance.job_id
        con = get_connection('default')   
        job = Job.fetch(job_id,connection=con)
        job.delete()
    except:
        print("Job not found")
    

    


