# authentication/urls.py
from django.urls import path
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    RequestResetPasswordView,
    ResetPasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify/email/', VerifyEmailView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('request-reset/password/', RequestResetPasswordView.as_view()),
    path('reset/password/', ResetPasswordView.as_view()),
]
