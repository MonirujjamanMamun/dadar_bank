from django.urls import path
from . views import DepositMoneyView, WithdrowMoneyView, LoanRequestView, TransactionReportView, PayLoanView, LoanListView, TransferMoneyView
urlpatterns = [
    path('deposite/', DepositMoneyView.as_view(), name='deposit_money'),
    path("withdrow/", WithdrowMoneyView.as_view(), name="withdraw_money"),
    path("loanrequest/", LoanRequestView.as_view(), name="loan_request"),
    path("transactionreport/", TransactionReportView.as_view(),
         name="transaction_report"),
    path("payloan/<int:loan_id>/", PayLoanView.as_view(), name="pay"),
    path("loanlist/", LoanListView.as_view(), name="loan_list"),
    path("transfer/", TransferMoneyView.as_view(), name="transfer"),
]
