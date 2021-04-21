# from __future__ import absolute_import, unicode_literals
# from celery import shared_task
# from time import sleep
# import twint 
# @shared_task
# def dene(x,y):
#     #user = "turk"
#     limit = 1000
#     search_keyword = "turk hack"
#     c = twint.Config()
#     c.Search = search_keyword
#     c.Since = "2020-01-01"
#     c.Elasticsearch = "http://127.0.0.1:9200"
#     twint.run.Search(c)

from .models import Task, ScheduledTask, ScheduledTaskInstance
from rq import get_current_job
from django_rq import job
import requests
import datetime 
from .elasticsearch import SearchElk,InsertElk
import twint
from django.utils import timezone,dateformat

#def add_tweet(keyword):


@job
def addTweetOnce(keyword):
    print("key",keyword)
    search = SearchElk()
    insert = InsertElk()
    job = get_current_job()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    res_before = search.get_count()
    #print("before",res_before)
    #before_length = len(res_before) if not isinstance(res_before,int) else 0

    task = Task.objects.create(
        job_id=job.get_id(),
        keyword=keyword,
    )
    insert.runOnce(keyword)

   

    #res_after = search.search(keyword)
    #print(res_after)
    #after_length = len(res_after) if not isinstance(res_after,int) else 0
    res_after = search.get_count()
    task.result = res_after-res_before #after_length-before_length
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
        result = res_after-res_before
    )
    return keyword + " " + str(res_after-res_before)+" Kayıt Eklendi"