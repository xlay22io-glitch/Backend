from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Lay, WithdrawRequest


class LaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lay
        fields = ['id', 'total_odds', 'stake_amount',
                  'win_payout', 'loss_payout', 'file_name', 'tip', 'match', 'created_at', 'status']


class LayCreateSerializer(serializers.Serializer):
    total_odd = serializers.FloatField()
    stake_amount = serializers.FloatField()
    win_payout = serializers.FloatField()
    file = serializers.ImageField()
    tip = serializers.CharField()
    match = serializers.CharField()
    loss_payout = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        if data['stake_amount'] > user.balance:
            raise serializers.ValidationError(
                {"detail": "Amount exceeds your current balance."})
        if data['file'].size > 2 * 1024 * 1024:
            raise serializers.ValidationError(
                {"detail": "File must be smaller than 2MB."})
        if data['file'].content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise serializers.ValidationError(
                {"detail": "Invalid image format."})
        return data


class WithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequest
        fields = ['amount', 'address']

    def validate_amount(self, value):
        user = self.context['request'].user
        if value > user.balance:
            raise serializers.ValidationError(
                _("You can't withdraw more than you have on account balance"))
        if value <= 0:
            raise serializers.ValidationError(_("Amount must be positive."))
        return value
