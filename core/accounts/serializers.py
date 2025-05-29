from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Lay, WithdrawRequest

class LaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lay
        fields = ['id', 'total_odds', 'stake_amount', 'win_payout', 'loss_payout', 'file_name']

class WithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequest
        fields = ['amount', 'address']

    def validate_amount(self, value):
        user = self.context['request'].user
        if value > user.balance:
            raise serializers.ValidationError(_("Amount exceeds current balance."))
        if value <= 0:
            raise serializers.ValidationError(_("Amount must be positive."))
        return value
