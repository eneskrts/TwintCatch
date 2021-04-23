from django.shortcuts import render
from kullanici.models import UserAlert
# Create your views here.
from django.urls import reverse,reverse_lazy
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from django.shortcuts import redirect,reverse
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import SimpleQueryString
import datetime
from django.contrib import messages
from .forms import SearchForm,AddAlertForm
import twint
from django.contrib.auth.models import User
from .elasticsearch import SearchElk
from .models import ScheduledTaskInstance,ScheduledTask
from django.utils import timezone
from django.urls import reverse,reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rq import cancel_job
@login_required(login_url=reverse_lazy('login'))
def SearchView(request):
    form = SearchForm(request.POST or None)
    form_add = AddAlertForm()
    searc = SearchElk()

    if request.method == "POST":

        if form.is_valid():
            try:
                data = searc.search(query=request.POST.get("search_key"))
                if data == 0:
                    data = "-"
                    return render(request, "search.html", context={"form": form, "search_results": data,'form_add':form_add})

            except Exception as e:
                data = "-"
            return render(request,"search.html",context={"form":form,"search_results":data,'form_add':form_add})
    return render(request,"search.html",context={"form":form,'form_add':form_add})
@login_required(login_url=reverse_lazy('login'))
def Search4Alert(request,id):
    try:
        task = ScheduledTask.objects.get(id=id)
        user = User.objects.get(username=request.user)
        usertaskalert = UserAlert.objects.get(user=user,task=task)
    except Exception as e:
        print(str(e),"Search4AlertView Hata")
        messages.success(request,"Kayıt Bulunamadı.",extra_tags="danger")
        return render(request,"search.html")
    form = SearchForm()
    form_add = AddAlertForm()
    searc = SearchElk()
    try:
        data = searc.search(query=task.keyword,exact_tarih=usertaskalert.seen.strftime("%Y-%m-%d %H:%M:%S"))
        usertaskalert.seen = timezone.now()
        usertaskalert.save()
        
        if data == 0:
            data = "-"
            return render(request, "search.html", context={"form": form, "search_results": data,'form_add':form_add})

    except Exception as e:
        print("Elastic Sunucusuna bağlanılamıyor",e)
        data = "-"
    return render(request,"search.html",context={"form":form,"search_results":data,'form_add':form_add})

def date_finder(request,form):
    switcher = {
        "all": 10000,
        "yil": 365,
        "ay": 30,
        "hafta": 7
    }
    return switcher.get(form.get("date_filter"))
    # if form.get("date_filter") == "all":
    #     return 10000
    # elif form.get("date_filter") == "yil":
    #     return 365
    # elif form.get("date_filter") == "ay":
    #     return 30
    # elif form.get("date_filter") == "hafta":
    #     return 7
    # else:
    #     adv_search_form = SearchForm()
    #     add_form = AddAlertForm()
    #     # message
    #     return render(request, "search.html", context={'form': adv_search_form,'form_add':add_form})

def search_field_select(form):
    arr = ["search^4"]
    #"tweet^2", "hashtags", "username", "name", "link"
    if form.get("field_tweet"):
        arr.append("tweet^2")
    if form.get("field_hashtag"):
        arr.append("hashtags")
    if form.get("field_username"):
        arr.append("username")
    if form.get("field_name"):
        arr.append("name")
    if form.get("field_link"):
        arr.append("link")
    if len(arr) <1:
        arr = ["tweet^2","search^4"]
    return arr
def add_detail_to_search(form):
    if form.get("field_kapsamli_arama"):
        arama_kelime = ""
        keywords = form.get("search_key")
        for kelime in keywords.split():
            arama_kelime+=kelime+"* "
        return arama_kelime
    return form.get("search_key")
def veya_sorgu(form):
    operator = "and"
    if form.get("field_and_vs_or"):
        operator = "or"
    return operator

@login_required(login_url=reverse_lazy('login'))
def DetailedSearchView(request):
    if request.method == "POST":
        form = request.POST
        searchkey = add_detail_to_search(form)
        date_select = date_finder(request,form)
        search_fields = search_field_select(form)
        default_operator = veya_sorgu(form)
        SearchObject = SearchElk()
        search_results = SearchObject.search(query=searchkey,default_operator=default_operator,tarih=date_select,fields=search_fields)
        adv_search_form = SearchForm(data=request.POST)
        form_add = AddAlertForm()
        return render(request, "search.html", context={'form': adv_search_form,"search_results": search_results,'form_add':form_add})
 











    adv_search_form = SearchForm()
    form_add = AddAlertForm()
    return render(request,"search.html",context={'form':adv_search_form,'form_add':form_add})

def scheduleInterval(aralik):
    switcher = {
        "ten_minute":10*60,
        "one_hour":60*60,
        "two_hour":120*60,
        "every_day":24*60*60,
        "every_week":7*24*60*60
    }
 
    intervalInt = switcher.get(aralik)
    return intervalInt

from .tasks import addTweetOnce,addTweetScheduled
from django.core.exceptions import PermissionDenied
import django_rq
from .models import Task

@login_required(login_url=reverse_lazy('login'))
def AddTweetView(request):

    if request.method == "GET":
        raise PermissionDenied
    if request.method == "POST":
        form_add = AddAlertForm(request.POST)
        if form_add.is_valid():

            search_key = form_add.cleaned_data.get("aranacak_ifade").lower()
            scheduled = form_add.cleaned_data.get("surekli_alarm")
            aralik = form_add.cleaned_data.get("aralik")
            aralik = scheduleInterval(aralik)
            if not scheduled:
                try:
                    tekrar = Task.objects.get(keyword=search_key)
                    messages.success(request,"Bu arama daha önce eklendi.",extra_tags="danger")
                    return HttpResponseRedirect(reverse_lazy('alerts'))
                except:
                    pass
                addTweetOnce.delay(search_key)

            else:
                try:
                    tekrar = ScheduledTask.objects.get(keyword=search_key)
                    messages.success(request,"Bu arama daha önce eklendi.",extra_tags="danger")
                    return HttpResponseRedirect(reverse_lazy('alerts'))
                except:
                    pass
                scheduler = django_rq.get_scheduler('default')

                job = scheduler.schedule(
                scheduled_time=datetime.datetime.now(),
                func=addTweetScheduled,
                args=[User.objects.all().first(),search_key],
                interval=aralik,
                repeat=5555555555)
            messages.success(request,"Ekleme Talebiniz Alındı",extra_tags="success")

    return HttpResponseRedirect(reverse_lazy('alerts'))
from django_rq import get_connection,get_scheduler
from rq.job import Job

@login_required(login_url=reverse_lazy('alerts'))
def DeleteTaskView(request,id):
    try:
        task = ScheduledTask.objects.get(id=id)
    except:
        messages.success(request,"Silinecek Görev Bulunamadı.")
        return HttpResponseRedirect(reverse_lazy('alerts'))
    
    try:
        task.delete()
        messages.success(request,"%s Kaydı Başarılı Bir Şekilde Durduruldu"%task.keyword,extra_tags="success")
    except Exception as e :
        print(str(e),"Cancel Job")
        messages.success(request,"Bu Bilgilerde Bir Kayıt Bulunamadı",extra_tags="danger")
        return HttpResponseRedirect(reverse_lazy('alerts'))
    return HttpResponseRedirect(reverse_lazy('alerts'))
    
