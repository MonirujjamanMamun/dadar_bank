
from django import forms
from . models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.blance_after_transaction = self.account.blance
        return super().save()


class DepositeForm(TransactionForm):
    def clean_amount(self):
        min_deposite_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposite_amount:
            raise forms.ValidationError(
                f'You need to deposite {min_deposite_amount}'
            )
        return amount


class WithdrowForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdrow = 100
        max_withdrow = 20000
        amount = self.cleaned_data.get('amount')
        blance = account.blance
        if amount < min_withdrow:
            raise forms.ValidationError(
                f'You can withdrow {min_withdrow} minimum.'
            )
        if amount > max_withdrow:
            raise forms.ValidationError(
                f'You can withdrow {max_withdrow} maximum.'
            )
        if amount > blance:
            raise forms.ValidationError(
                f"You don't have enough Balance. Your Balance is {blance} "
            )
        return amount


class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount


class TransferMoneyForm(forms.Form):
    amount = forms.DecimalField()
    to_user_id = forms.IntegerField()
