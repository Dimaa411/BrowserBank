from django.shortcuts import render, redirect
from main.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordResetCompleteView

# Представлення для введення email
def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Перевірка на наявність користувача з таким email
            user = User.objects.get(email=email)

            # Генерація токену для відновлення пароля
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())

            # Формуємо посилання для скидання пароля (https замість http)
            reset_link = f'https://{get_current_site(request).domain}/reset/{uid}/{token}/'

            # Створюємо повідомлення для email
            subject = 'Відновлення пароля'
            message = render_to_string('password_reset_email.html', {
                'reset_link': reset_link,
                'user': user
            })

            # Надсилаємо email з посиланням для відновлення пароля
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            # Перенаправляємо на сторінку підтвердження
            return redirect('password_reset_done')

        except User.DoesNotExist:
            # Якщо email не знайдено, показуємо помилку
            return render(request, 'reset_password.html', {'error': 'Цей email не знайдено.'})

    # Якщо запит GET, просто відображаємо форму
    return render(request, 'reset_password.html')


# Представлення для скидання пароля за токеном
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                # Перенаправлення на головну сторінку після успішної зміни пароля
                return redirect('main_page')  # Використовуйте ім'я вашого маршруту для головної сторінки
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        return redirect('password_reset_invalid')  # Це можна реалізувати для обробки помилки, якщо токен недійсний.


def index(request):
    message = request.GET.get('message')
    return render(request, 'index.html', {'message': message})


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {"error_message": "Емейл вже зареєстрований"})

        if User.objects.filter(username=username).exists():  # Замінили "name" на "username"
            return render(request, "register.html", {"error_message": "Ім'я користувача вже існує"})

        if not username:
            return render(request, "register.html", {"error_message": "Ім'я користувача повинно бути задано"})

        if password != confirm_password:
            return render(request, "register.html", {"error_message": "Паролі не співпадають"})

        new_user = User.objects.create_user(username=username, email=email, password=password)
        login(request, new_user)
        return redirect(f"/?message=Вітаємо, ви успішно зареєстровані!")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(f"/?message=Вітаємо вас, {User.username}")
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


def password_reset_invalid(request):
    return render(request, 'password_reset_invalid.html')

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_complete(request):
    return PasswordResetCompleteView.as_view()(request)