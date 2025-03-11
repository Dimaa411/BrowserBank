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
from django.db.models.signals import post_save
from django.dispatch import receiver
from transactions.models import Account  

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            reset_link = f'http://{get_current_site(request).domain}/reset/{uid}/{token}/'

            subject = 'Відновлення пароля'
            message = render_to_string('password_reset_email.html', {
                'reset_link': reset_link,
                'user': user
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return redirect('password_reset_done')

        except User.DoesNotExist:
            return render(request, 'reset_password.html', {'error': 'Цей email не знайдено.'})

    return render(request, 'reset_password.html')

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
                return redirect('main_page')
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        return redirect('password_reset_invalid')


from transactions.models import Account


def index(request):
    if request.user.is_authenticated:
        try:
            account = Account.objects.get(user=request.user)
            balance = account.balance
            print(f"Баланс для {request.user.username}: {balance}")
        except Account.DoesNotExist:
            balance = 0
    else:
        balance = 0

    return render(request, 'index.html', {'balance': balance})


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
            return redirect(f"/?message=Вітаємо вас, {user.username}")
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
