from decimal import Decimal
from django.utils.timezone import now
from .models import WeeklyBonus
from .utils import get_week_range  # the helper we wrote before


def reset_weekly_bonuses():
    """Called every Monday 00:01 via django-crontab."""
    today = now().date()
    start, end = get_week_range(today)
    new_start = start
    new_end = end

    # Iterate through all users’ bonuses
    for bonus in WeeklyBonus.objects.all():
        user = bonus.user
        # Apply reward to user’s wallet if you store it on user
        if bonus.weekly_reward and bonus.weekly_reward > 0:
            # convert float -> Decimal safely, then add
            # user.balance is FloatField
            current = Decimal(str(user.balance or 0))
            new_balance = (current + Decimal(bonus.weekly_reward))
            # keep the field type consistent
            user.balance = float(new_balance)
            user.save(update_fields=["balance"])

        # reset the weekly counters (if that's your desired behavior here)
        bonus.weekly_balance = Decimal("0")
        bonus.weekly_reward = Decimal("0")
        bonus.save(update_fields=["weekly_balance", "weekly_reward"])

    print(f"✅ Weekly bonuses reset on {today}")
