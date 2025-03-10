from django.urls import path
from . import views

urlpatterns = [
    path('transfer/', views.transfer_funds, name='transfer_funds'),

]
