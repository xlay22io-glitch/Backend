# authentication/urls.py
from django.urls import path
from .views import RegisterView, VerifyEmailView, LoginView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify/email/', VerifyEmailView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
]
