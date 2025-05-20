# authentication/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import CustomUser
from .services import EmailService

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"detail": "Passwords do not match"})
        if len(data['password']) < 8:
            raise serializers.ValidationError({"detail": "Password too short"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Email is not verified"})

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        self.token = data["refresh"]
        return data

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError({"detail": "Invalid token"})

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            self.user = None
        return value

    def save(self, request):
        if self.user:
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))
            token = default_token_generator.make_token(self.user)
            reset_url = f"{request.build_absolute_uri('/auth/reset/password/')}?uid={uid}&token={token}"
            EmailService.send_password_reset_email(self.user.email, reset_url)

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            self.user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError({"detail": "Wrong User ID or User does not exist!"})

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError({"detail": "Invalid or expired token!"})

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"detail": "Passwords do not match!"})

        if len(data["password"]) < 8:
            raise serializers.ValidationError({"detail": "Password too weak!"})

        return data

    def save(self):
        self.user.set_password(self.validated_data["password"])
        self.user.save()