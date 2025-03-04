from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User

def main_page(request):
    return render(request, 'index.html')

def login_page(request):  # Змінено ім'я на login_page
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Користувач вже існує'})

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Паролі не співпадають'})

        try:
            user = User.objects.create_user(username=username, password=password)
            auth_login(request, user)
            return redirect('main_page')
        except Exception as e:
            print(f"Error: {e}")
            return render(request, 'register.html', {'error': 'Не вдалося створити користувача'})

    return render(request, 'register.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('main_page')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Змінено на auth_login
            print('Successfully logged in')
            return redirect('main_page')
        else:
            print('Login failed')

        return render(request, 'authorization.html', {'error': 'Invalid credentials'})

    return render(request, 'authorization.html')

def user_logout(request):
    logout(request)
    return redirect('main_page')

def dashboard(request):
    return render(request, 'dashboard.html')
