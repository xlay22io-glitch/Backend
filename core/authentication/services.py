# authentication/utils.py
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

class EmailService:

    def send_activation_email(user, request):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = f"{settings.FRONTEND_URL}/auth/verify?uid={uid}&token={token}"
        message = f"Click the link to verify your email: {verify_url}"
        send_mail(
            "Verify your account",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    @staticmethod
    def send_password_reset_email(email, reset_url):

        message = f"Click the link below to reset your password:\n{reset_url}"
        send_mail(
            "Reset Your Password",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
