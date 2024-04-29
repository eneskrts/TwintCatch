


from django.urls import path,include
from .views import SearchView,DetailedSearchView,AddTweetView,Search4Alert,DeleteTaskView
app_name = 'TwintSearch'
urlpatterns = [

    path('',SearchView,name="search"),
    path('gelismis-arama',DetailedSearchView,name="detailed-search"),
    path('yeni-arama',AddTweetView,name="add-search"),
    path('alert-search/<int:id>',Search4Alert,name="alert-search"),
    path('delete-task/<int:id>',DeleteTaskView,name='delete-task')
]
