from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
]
