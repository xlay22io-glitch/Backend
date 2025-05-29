import pytest
from django.urls import reverse
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def create_user_with_balance(db):
    user = User.objects.create_user(
        email="testuser@example.com",
        password="testpassword123"
    )
    user.balance = 1.0
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def auth_headers(create_user_with_balance):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"email": "testuser@example.com", "password": "testpassword123"},
        format="json"
    )
    print("LOGIN RESPONSE:", response.status_code, response.content.decode())

    if response.status_code != 200:
        raise Exception(f"Login failed! Status: {response.status_code}, Content: {response.content.decode()}")

    token = response.data["access"]
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

@pytest.mark.django_db
def test_withdraw_valid(client, create_user_with_balance, auth_headers):
    url = reverse("withdraw")
    payload = {"amount": 0.5, "address": "test_address"}
    response = client.post(url, data=payload, **auth_headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "We received your request! We will get back to you shortly!"

@pytest.mark.django_db
def test_withdraw_invalid_amount(client, create_user_with_balance, auth_headers):
    url = reverse("withdraw")
    payload = {"amount": 9999, "address": "test_address"}
    response = client.post(url, data=payload, **auth_headers)
    assert response.status_code == 400
