from django.core.management.base import BaseCommand
from accounts.models import DepositAddress, DepositRotation

class Command(BaseCommand):
    help = "Seed initial 10 deposit addresses and deposit rotation"

    def handle(self, *args, **kwargs):
        # Clear old data
        DepositAddress.objects.all().delete()
        DepositRotation.objects.all().delete()

        for i in range(1, 11):
            DepositAddress.objects.create(
                address=f"Deposit_Address_{i}",
                index=i
            )

        DepositRotation.objects.create(current_index=1)

        self.stdout.write(self.style.SUCCESS("✅ Seeded 10 deposit addresses and initialized rotation."))
