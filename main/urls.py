from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_page'),
    path('login/', views.login_view, name='login'),  # Змінили на login_page
    #path('register/', views.register, name='register'),
    #path('user_login/', views.user_login, name='user_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.some_view, name='dashboard'),
]
