from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.some_view, name='dashboard'),
    path('reset_password/', views.password_reset, name='reset_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset_password/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),

]
