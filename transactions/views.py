import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Account, Transaction
from decimal import Decimal
from .models import Account
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
def deposit(request):
    if request.method == "POST":
        amount = request.POST.get('amount')

        if amount:
            try:
                amount = Decimal(amount)
                if amount <= 0:

                    return render(request, 'deposit.html', {'error': 'Сума має бути більшою за 0'})

                account = Account.objects.get(user=request.user)

                if amount > account.balance:
                    return render(request, 'deposit.html', {'error': 'Депозит не може бути більшим за ваш баланс'})

                account.balance += amount
                account.save()

                return redirect('main_page')

            except ValueError:
                return render(request, 'deposit.html', {'error': 'Невірна сума депозита'})
            except Account.DoesNotExist:
                return render(request, 'deposit.html', {'error': 'Акаунт не знайдений'})
        else:
            return render(request, 'deposit.html', {'error': 'Будь ласка, введіть суму депозиту'})

    return render(request, 'deposit.html')



def send_transaction_receipt(receiver_email, sender, receiver, amount):
    subject = "Квитанція про переказ коштів"
    message = f"""
        Шановний {receiver.username},

        Ви отримали переказ коштів від {sender.username}.

        Сума: {amount} грн

        Дякуємо за використання нашого сервісу!

        З повагою,  
        TOPBANK
    """
    subject2 = "Квитанція про переказ коштів"
    message2 = f"""
            Шановний {sender.username},

            Ви оформили переказ коштів користувачу {receiver.username}.

            Сума: {amount} грн

            Дякуємо за використання нашого сервісу!

            З повагою,  
            TOPBANK
        """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver_email])
    send_mail(subject2, message2, settings.EMAIL_HOST_USER, [sender.email])


def transfer_funds(request):

    user_transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(
        receiver=request.user)

    if request.method == "POST":
        receiver_username = request.POST.get("receiver")
        amount = request.POST.get("amount")

        try:
            amount = Decimal(amount)
            sender = request.user
            sender_account = Account.objects.get(user=sender)
            receiver = User.objects.get(username=receiver_username)
            receiver_account = Account.objects.get(user=receiver)

            if sender_account.balance >= amount:
                confirmation_code = random.randint(100000, 999999)
                request.session["transfer_code"] = confirmation_code
                request.session["transfer_data"] = {
                    "receiver": receiver_username,
                    "amount": str(amount)
                }


                send_mail(
                    "Код підтвердження переказу",
                    f"Ваш код підтвердження: {confirmation_code}",
                    settings.EMAIL_HOST_USER,
                    [sender.email]
                )

                return redirect("confirm_transfer")

            else:
                messages.error(request, "Недостатньо коштів для переказу")
        except User.DoesNotExist:
            messages.error(request, "Користувача не знайдено")
        except ValueError:
            messages.error(request, "Некоректна сума")
        except Exception as e:
            messages.error(request, f"Помилка: {e}")

        return redirect("transfer_funds")

    return render(request, "transfer.html", {"user_transactions": user_transactions})


@login_required
def confirm_transfer(request):
    if request.method == "POST":
        entered_code = request.POST.get("code")
        stored_code = request.session.get("transfer_code")
        transfer_data = request.session.get("transfer_data")

        if not stored_code or not transfer_data:
            messages.error(request, "Сесія завершена, спробуйте ще раз.")
            return redirect("transfer_funds")

        if str(entered_code) == str(stored_code):
            try:
                sender = request.user
                sender_account = Account.objects.get(user=sender)
                receiver = User.objects.get(username=transfer_data["receiver"])
                receiver_account = Account.objects.get(user=receiver)
                amount = Decimal(transfer_data["amount"])

                sender_account.balance -= amount
                receiver_account.balance += amount
                sender_account.save()
                receiver_account.save()


                Transaction.objects.create(sender=sender, receiver=receiver, amount=amount, status="completed")


                if receiver.email:
                    send_transaction_receipt(receiver.email, sender, receiver, amount)

                messages.success(request, f"Переказ {amount} грн підтверджено!")
                del request.session["transfer_code"]
                del request.session["transfer_data"]
                return redirect("transfer_funds")

            except Exception as e:
                messages.error(request, f"Помилка при підтвердженні: {e}")
                return redirect("transfer_funds")

        else:
            messages.error(request, "Невірний код підтвердження")

    return render(request, "confirm_transfer.html")
