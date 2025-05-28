import pytest
from rest_framework.test import APIClient
from accounts.models import DepositAddress, DepositRotation

@pytest.mark.django_db
def test_deposit_address_rotation(django_user_model):
    user = django_user_model.objects.create_user(email="test@example.com", password="pass1234")
    
    DepositAddress.objects.all().delete()
    DepositRotation.objects.all().delete()

    for i in range(1, 11):
        DepositAddress.objects.create(address=f"Deposit_Address_{i}", index=i)
    DepositRotation.objects.create(current_index=1)

    client = APIClient()
    client.force_authenticate(user=user)

    for expected_index in [1, 2, 3]:
        response = client.get("/api/v1/account/deposit/generate/")
        assert response.status_code == 200
        assert response.data["address"] == f"Deposit_Address_{expected_index}"

@pytest.mark.django_db
def test_deposit_rotation_wraps_around(django_user_model):
    user = django_user_model.objects.create_user(email="loop@example.com", password="pass1234")

    DepositAddress.objects.all().delete()
    DepositRotation.objects.all().delete()

    for i in range(1, 11):
        DepositAddress.objects.create(address=f"Deposit_Address_{i}", index=i)
    DepositRotation.objects.create(current_index=1)

    client = APIClient()
    client.force_authenticate(user=user)

    for expected_index in range(1, 11):
        res = client.get("/api/v1/account/deposit/generate/")
        assert res.data["address"] == f"Deposit_Address_{expected_index}"

    res = client.get("/api/v1/account/deposit/generate/")
    assert res.data["address"] == "Deposit_Address_1"
