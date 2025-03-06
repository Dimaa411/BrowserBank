from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from main.models import User

def index(request):
    message = request.GET.get('message') 
    return render(request, 'index.html', {'message': message})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(f"/?message=Вітаємо вас, {User.name}")
        else:
            return render(request, "login.html", {"error_message": "Невірний логін або пароль"})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('/')



def some_view(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html")
    else:
        return HttpResponseRedirect("/login/")
