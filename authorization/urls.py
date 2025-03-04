from django.urls import path
from . import views

urlpatterns = [
    path('', views.authorization, name='index'),
]