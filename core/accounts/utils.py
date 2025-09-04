# utils.py
from django.db import transaction
from decimal import Decimal
import datetime
from django.utils.timezone import now


def get_week_range(date=None):
    """Returns Monday–Sunday date range for the given date (default today)."""
    if date is None:
        date = now().date()
    start = date - datetime.timedelta(days=date.weekday())  # Monday
    end = start + datetime.timedelta(days=6)                # Sunday
    return start, end


@transaction.atomic
def apply_weekly_delta(*, user, reference_date, delta):
    """
    Adjust user's WeeklyBonus for the week that includes reference_date.
    Recalculate reward after applying delta.
    """
    # ⬇️ Import here to avoid models<->utils circular import at import time
    from .models import WeeklyBonus

    week_start, week_end = get_week_range(reference_date)
    bonus, _ = WeeklyBonus.objects.select_for_update().get_or_create(
        user=user, week_start=week_start, week_end=week_end
    )

    bonus.calculate_reward()
    bonus.save()
