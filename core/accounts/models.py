import uuid
from django.db import models
from authentication.models import CustomUser as User


class Lay(models.Model):
    STATUS_CHOICES = [
        ("declined", "Declined"),
        ("pending", "Pending"),
        ("approved", "Approved"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lays')
    total_odds = models.FloatField()
    stake_amount = models.FloatField()
    win_payout = models.FloatField()
    loss_payout = models.FloatField()
    file_name = models.CharField(max_length=255)
    file = models.ImageField(upload_to='lays/')

    match = models.CharField(max_length=255, default="")
    tip = models.CharField(max_length=255, default="")
    loss_payout = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )


class DepositAddress(models.Model):
    address = models.CharField(max_length=255, unique=True)
    index = models.PositiveIntegerField(unique=True)


class DepositRotation(models.Model):
    current_index = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Deposit Rotation"


class WithdrawRequest(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="withdraw_requests")
    amount = models.FloatField()
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
