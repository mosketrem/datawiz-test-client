from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'client'
urlpatterns = [
    path('', cache_page(settings.CACHE_AGE)(views.index), name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]
