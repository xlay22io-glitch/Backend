import io
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image

from authentication.models import CustomUser

@pytest.fixture
def create_user(db):
    return CustomUser.objects.create_user(email="testuser@example.com", password="testpass123", balance=100)

@pytest.fixture
def auth_client(create_user):
    client = APIClient()
    client.force_authenticate(user=create_user)
    return client

def generate_image_file(name='test.jpg'):
    image = Image.new('RGB', (100, 100))
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='JPEG')
    byte_arr.seek(0)
    return byte_arr

def test_calculator_success(auth_client):
    image_file = generate_image_file()
    response = auth_client.post(
        reverse('calculator'),
        {
            "total_odd": 5,
            "stake_amount": 10,
            "win_payout": 50,
            "file": image_file,
            "all_data_true": True
        },
        format='multipart'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {}

def test_missing_file(auth_client):
    response = auth_client.post(
        reverse('calculator'),
        {
            "total_odd": 5,
            "stake_amount": 10,
            "win_payout": 50,
            "all_data_true": True
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "File field is required!"}

def test_invalid_data(auth_client):
    response = auth_client.post(
        reverse('calculator'),
        {
            "total_odd": 5,
            "stake_amount": 1000,
            "win_payout": 5000,
            "all_data_true": False
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Data is not valid!"}

def test_unauthenticated_user():
    client = APIClient()
    response = client.post(reverse('calculator'), {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication credentials were not provided."}
