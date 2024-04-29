from __future__ import absolute_import, unicode_literals
from celery import shared_task
from time import sleep
import twint


from .models import Task, ScheduledTask, ScheduledTaskInstance
from rq import get_current_job
from django_rq import job
import datetime
from .es import SearchElk,InsertElk
from django.utils import timezone,dateformat


@job
def addTweetOnce(keyword):
    search = SearchElk()
    insert = InsertElk()
    job = get_current_job()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    res_before = search.get_count()

    task = Task.objects.create(
        job_id=11111,
        keyword=keyword,
    )
    insert.runOnce(keyword)
    res_after = search.get_count()
    task.result = res_after-res_before
    task.save()
    return keyword + " " + str(res_after-res_before) + " Kayıt Eklendi"


@job
def addTweetScheduled(user,keyword):
    insert = InsertElk()
    search = SearchElk()
    """
    This creates a ScheduledTask instance for each group of
    scheduled task - each time this scheduled task is run
    a new instance of ScheduledTaskInstance will be created
    """
    job = get_current_job()

    task, created = ScheduledTask.objects.get_or_create(
        job_id=job.get_id(),
        user=user,
        keyword=keyword
    )
    res_before = search.get_count()
    if not created:
        since = task.created_on.strftime("%Y-%m-%d %H:%M:%S")
        insert.runScheduled(keyword,since=since)
    else:
        insert.runScheduled(keyword)
    task.created_on = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
    task.save()
    res_after = search.get_count()
    ScheduledTaskInstance.objects.create(
        scheduled_task=task,
        result=res_after-res_before
    )
    return keyword + " " + str(res_after-res_before)
