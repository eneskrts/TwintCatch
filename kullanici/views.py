from django.shortcuts import render
from django.contrib.auth.models import User
# Create your views here.
from django.contrib.auth import login,logout
from django.contrib import messages
from .forms import LoginForm
from django.urls import reverse,reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import Sum
from TwintSearch.models import ScheduledTaskInstance,ScheduledTask
from .models import UserAlert
from TwintSearch.es import SearchElk


def LoginView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            messages.success(request,"Başarıyla Giriş Yaptınız. Anasayfaya Yönlendiriliyorsunuz.")
            username = request.POST.get("username")
            user = User.objects.get(username=username)
            login(request, user)
            messages.success(request, "Giriş Yaptığınız İçin Teşekkürler %s"
                             %user.username, extra_tags="success")
            return HttpResponseRedirect("/")

        messages.success(request, "Kullanıcı Adı veya Parola Hatalı.", extra_tags="danger")
        return render(request, "login.html", context={'form': form})
    else:

        form = LoginForm()
        return render(request,"login.html",context={'form': form})


@login_required(login_url=reverse_lazy('login'))
def LogoutView(request):
    messages.success(request,"Başarıyla Çıkış Yaptınız",extra_tags="success")
    logout(request)
    return HttpResponseRedirect("/")


@login_required(login_url=reverse_lazy('login'))
def AlertView(request):
    user = request.user
    search = SearchElk()
    scheduled_tasks = ScheduledTask.objects.all()
    table_data = []
    for task in scheduled_tasks:

        usertask, created = UserAlert.objects.get_or_create(user=user,task=task)
        if created:
            date = (datetime.datetime.now() - datetime.timedelta(days=100000))
            usertask.seen = date
            usertask.save()
        instances = ScheduledTaskInstance.objects.filter(scheduled_task=task,created_on__gte=usertask.seen).aggregate(Sum('result'))

        if instances.get("result__sum"):
            table_data.append({
                'task_id':task.id,
                'keyword':task.keyword,
                'tarih':ScheduledTaskInstance.objects.filter(scheduled_task=task,created_on__gte=usertask.seen).latest('created_on').created_on,
                'bildirim_sayi':instances.get('result__sum')

            })

    return render(request,"alerts.html",context={'table_data':table_data})


