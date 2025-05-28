from rest_framework import serializers
from .models import Lay

class LaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lay
        fields = ['id', 'total_odds', 'stake_amount', 'win_payout', 'loss_payout', 'file_name']
