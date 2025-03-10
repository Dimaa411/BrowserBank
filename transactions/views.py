from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Account, Transaction
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

@login_required
def transfer_funds(request):
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
                sender_account.balance -= amount
                receiver_account.balance += amount
                sender_account.save()
                receiver_account.save()

                Transaction.objects.create(sender=sender, receiver=receiver, amount=amount, status='completed')
                messages.success(request, f" Успішний переказ {amount} від {sender.username} до {receiver.username}")
            else:
                messages.error(request, " Недостатньо коштів для переказу")
        except User.DoesNotExist:
            messages.error(request, " Користувача не знайдено")
        except ValueError:
            messages.error(request, " Некоректна сума")
        except Exception as e:
            messages.error(request, f" Помилка: {e}")

        return redirect("transfer_funds")

    user_transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(
        receiver=request.user)
    user_transactions = user_transactions.order_by('-date')

    return render(request, "transfer.html", {'user_transactions': user_transactions})

