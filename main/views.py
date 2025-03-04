from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, 'main_page.html', {'error': 'User already exists'})

        user = User.objects.create_user(username=username, password=password)
        user.save()

        login(request, user)
        return redirect('login')  # Оновлено, щоб уникнути помилки

    return render(request, 'main_page.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('authorization')

        return render(request, 'registration.html', {'error': 'Invalid credentials'})

    return render(request, 'main_page.html')

def user_logout(request):
    logout(request)
    return redirect('login')
