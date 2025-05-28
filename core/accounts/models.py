import uuid
from django.db import models
from authentication.models import CustomUser as User

class Lay(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('history', 'History'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lays')
    total_odds = models.FloatField()
    stake_amount = models.FloatField()
    win_payout = models.FloatField()
    loss_payout = models.FloatField()
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

class DepositAddress(models.Model):
    address = models.CharField(max_length=255, unique=True)
    index = models.PositiveIntegerField(unique=True)

class DepositRotation(models.Model):
    current_index = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Deposit Rotation"
