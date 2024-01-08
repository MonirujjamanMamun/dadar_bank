from typing import Any
from django.contrib import admin
from .models import Transaction
from . views import transaction_mail
# Register your models here.

# admin.site.register(Transaction)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'blance_after_transaction',
                    'transaction_type', 'loan_approve']

    def save_model(self, request, obj, form, change):
        obj.account.blance += obj.amount
        obj.blance_after_transaction = obj.account.blance
        obj.account.save()
        transaction_mail(
            'Admin Loan Approve', 'transaction/loan_approval.html', obj.amount, obj.account.user)
        super().save_model(request, obj, form, change)
