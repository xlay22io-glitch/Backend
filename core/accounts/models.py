import uuid
from decimal import Decimal
from django.db import models,  transaction
from authentication.models import CustomUser as User
from .utils import apply_weekly_delta


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

    def _status_delta(self, status) -> Decimal:
        """Map a status to its effect on weekly_balance."""
        if status == "approved":
            return Decimal(str(self.win_payout))          # +win
        if status == "declined":
            return Decimal(str(-self.stake_amount))       # -stake
        # pending/others: no effect
        return Decimal("0")

    def save(self, *args, **kwargs):
        # detect old status if updating
        old_status = None
        if self.pk:
            try:
                old_status = Lay.objects.only("status").get(pk=self.pk).status
            except Lay.DoesNotExist:
                old_status = None

        with transaction.atomic():
            super().save(*args, **kwargs)  # persist new status/amounts first

            # If status changed, adjust the weekly balance for the week of THIS lay (created_at week)
            if old_status != self.status:
                # Use the lay's created_at week (not "now"), so history is correct
                ref_date = (self.created_at.date()
                            if self.created_at else None)

                # revert old effect, then apply new
                if old_status:
                    apply_weekly_delta(
                        user=self.user,
                        reference_date=ref_date,
                        delta=(-self._status_delta(old_status))
                    )
                apply_weekly_delta(
                    user=self.user,
                    reference_date=ref_date,
                    delta=(self._status_delta(self.status))
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


class WeeklyBonus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weekly_bonuses")
    week_start = models.DateField()
    week_end = models.DateField()

    weekly_balance = models.DecimalField(
        max_digits=12, decimal_places=6, default=0)
    weekly_reward = models.DecimalField(
        max_digits=12, decimal_places=6, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "week_start", "week_end")

    def calculate_reward(self):
        # Use Decimal arithmetic
        bal = Decimal(self.weekly_balance)
        if bal < 0:
            self.weekly_reward = (-bal) / Decimal("5")  # 20%
        else:
            self.weekly_reward = Decimal("0")
        return self.weekly_reward

    def reset_week(self, new_start, new_end):
        """
        Reset balance/reward for new week but carry over reward to user’s account.
        """
        # Add reward to user balance here if you store balance on user
        self.week_start = new_start
        self.week_end = new_end
        self.weekly_balance = 0
        self.weekly_reward = 0
        self.save()
