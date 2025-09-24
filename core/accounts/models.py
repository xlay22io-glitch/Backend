import uuid
from decimal import Decimal
from django.db import models,  transaction
from authentication.models import CustomUser as User
from .utils import apply_weekly_delta


class LayStatus(models.TextChoices):
    DECLINED = "declined", "Declined"
    PENDING = "pending",  "Pending"
    APPROVED = "approved", "Approved"


class Lay(models.Model):

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
        choices=LayStatus.choices,
        default=LayStatus.PENDING,
    )

    def _status_weekly_delta(self, status) -> Decimal:
        if status == "approved":
            return Decimal(str(self.win_payout)) - Decimal(str(self.stake_amount))
        if status == "declined":
            return -Decimal(str(self.stake_amount))
        return Decimal("0")

    # ── Wallet (available balance) credit on a given status
    # Declined: +loss_payout
    # Approved: +win_payout
    def _status_wallet_credit(self, status) -> Decimal:
        if status == "approved":
            return Decimal(str(self.win_payout))
        if status == "declined":
            return Decimal(str(self.loss_payout or "0"))
        return Decimal("0")

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            try:
                old_status = Lay.objects.only("status").get(pk=self.pk).status
            except Lay.DoesNotExist:
                old_status = None

        with transaction.atomic():
            # lock the user row to make wallet math race-safe
            user = User.objects.select_for_update().get(pk=self.user_id)

            super().save(*args, **kwargs)  # persist changes to this Lay

            # Only act when status actually changed
            if old_status != self.status:
                ref_date = self.created_at.date() if self.created_at else None

                # 1) WEEKLY BALANCE change: revert old effect, apply new
                if old_status:
                    apply_weekly_delta(
                        user=self.user,
                        reference_date=ref_date,
                        delta=-self._status_weekly_delta(old_status),
                    )
                apply_weekly_delta(
                    user=self.user,
                    reference_date=ref_date,
                    delta=self._status_weekly_delta(self.status),
                )

                # 2) USER WALLET (available balance): credit difference
                old_credit = self._status_wallet_credit(
                    old_status) if old_status else Decimal("0")
                new_credit = self._status_wallet_credit(self.status)
                diff = new_credit - old_credit

                current = Decimal(str(user.balance or 0))
                user.balance = float(current + diff)
                user.save(update_fields=["balance"])


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
