from django.urls import path
from .views import AccountInfoView, GenerateDepositAddressView, WithdrawRequestView

urlpatterns = [
    path('info/', AccountInfoView.as_view(), name='account-info'),
    path("deposit/generate/", GenerateDepositAddressView.as_view(), name="deposit-generate"),
    path("withdraw/", WithdrawRequestView.as_view(), name="withdraw"),
]
