from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from . models import Transaction
from . constants import DEPOSITE, WITHDRAWAL, LOAN, LOAN_PAID, TRANSFER, RECEIVED
from django.contrib import messages
from . forms import WithdrowForm, LoanRequestForm, DepositeForm, TransferMoneyForm
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from account.models import UserBankAccount
# Create your views here.


def transaction_mail(subject, template, amount, user):

    message = render_to_string(template, {
        'user': user,
        'amount': amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()


class TransactionCreatView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transaction/transaction_form.html'
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context


class DepositMoneyView(TransactionCreatView):
    title = 'Deposit'
    form_class = DepositeForm

    def get_initial(self):
        initial = {'transaction_type': DEPOSITE}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        # amount = 200, tar ager blance = 0 taka new blance = 0+200 = 200
        account.blance += amount
        account.save(
            update_fields=[
                'blance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        transaction_mail(
            "Deposit Messages", 'transaction/deposite_email.html', amount, self.request.user)

        return super().form_valid(form)


class WithdrowMoneyView(TransactionCreatView):
    title = 'Withdrow'
    form_class = WithdrowForm

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        is_bankrupt = UserBankAccount.objects.filter(
            is_bankrupt=True)
        if not is_bankrupt:
            account.blance -= amount
            account.save(
                update_fields=['blance']
            )
            messages.success(self.request, f"{amount} Withdrow Successfully.")
            transaction_mail(
                'Withdrow Messages', 'transaction/withdrow_email.html', amount, self.request.user)
        else:
            messages.error(self.request, 'Bank is bankrupt.')
        transaction_mail(
            'Withdrow Messages', 'transaction/withdrow_email.html', amount, self.request.user)
        return super().form_valid(form)


class LoanRequestView(TransactionCreatView):
    title = 'Request For Loan'
    form_class = LoanRequestForm

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type=LOAN, loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse('Opps, You crose your limite')
        messages.success(
            self.request, f"Your {amount} succesfully send to admin for approvel.")

        transaction_mail(
            'Loan Request Messages', 'transaction/loan_email.html', amount, self.request.user)
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transaction/transaction_report.html'
    model = Transaction
    blance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.blance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.blance = self.request.user.account.blance
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, loan_id)
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.blance:
                user_account.blance -= loan.amount
                loan.blance_after_transaction = user_account.blance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect()
            else:
                messages.error(self.request, f"Your haven't enough money.")
                return redirect()


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transaction/loan_request.html"
    # template file a object/appname ar poribota ai name deya for loop clano jay
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(
            account=user_account, transaction_type=LOAN)
        print(queryset)
        return queryset


class TransferMoneyView(View):
    template_name = 'transaction/transfer_money.html'

    def get(self, request):
        form = TransferMoneyForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TransferMoneyForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            to_user_id = form.cleaned_data['to_user_id']

            current_user = request.user.account
            # print("Current User blance Before Transfer:",
            #       current_user.user.email)

            try:
                to_user = UserBankAccount.objects.get(
                    account_no=to_user_id)
                min_blance_to_transfer = 100
                max_blance_to_transfer = 20000

                if current_user.blance <= 0:
                    messages.error(
                        request,
                        'you have not enough blance to transfer'
                    )
                    return render(request, self.template_name, {'form': form, 'title': 'Transfer Money'})

                if amount < min_blance_to_transfer:
                    messages.error(
                        request,
                        f'You need to transfer at least {min_blance_to_transfer} $'
                    )
                    return render(request, self.template_name, {'form': form, 'title': 'Transfer Money'})

                if amount > max_blance_to_transfer and amount <= current_user.blance:
                    messages.error(
                        request,
                        f'You can transfer at most {max_blance_to_transfer} $'
                    )
                    return render(request, self.template_name, {'form': form, 'title': 'Transfer Money'})

                if amount > current_user.blance:
                    messages.error(
                        request,
                        f'You have {current_user.blance} $ in your account. '
                        'You can not transfer more than your account blance'
                    )
                    return render(request, self.template_name, {'form': form, 'title': 'Transfer Money'})

                # Deduct the amount from current user's blance
                current_user.blance -= amount
                current_user.save()

                transaction_from = Transaction.objects.create(
                    account=current_user,
                    amount=amount,
                    blance_after_transaction=current_user.blance,
                    transaction_type=TRANSFER,  # Set the correct value
                    # loan_approve=False  # Set the correct value
                )
                transaction_to = Transaction.objects.create(
                    account=to_user,
                    amount=amount,
                    blance_after_transaction=to_user.blance,
                    transaction_type=RECEIVED,  # Set the correct value
                    # loan_approve=False  # Set the correct value
                )

                # print(
                #     f"blance After Transaction: {transaction.blance_after_transaction}")

                to_user.blance += amount
                to_user.save()

                messages.success(
                    request,
                    f'Transfer of {"{:,.2f}".format(float(amount))}$ successful'
                )
                # print(current_user.blance)
                # print(amount)
                # print(current_user.user.email)
                transaction_mail('Transfer Message',
                                 'transaction/transfer_email.html', amount, current_user.user)
                transaction_mail('Received Message',
                                 'transaction/received_email.html', amount, to_user.user)

            except UserBankAccount.DoesNotExist:
                messages.error(
                    request, 'User account not found. Please check the account number.')

            return render(request, self.template_name, {'form': form, 'title': 'Transfer Money'})
        return render(request, self.template_name, {'form': form, 'title': 'Transfer Money'})
