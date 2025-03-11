from django.urls import path
from . import views

urlpatterns = [
    path('transfer/', views.transfer_funds, name='transfer_funds'),
    path('confirm-transfer/', views.confirm_transfer, name='confirm_transfer'),
    path('deposit/', views.deposit, name='deposit'),
]
