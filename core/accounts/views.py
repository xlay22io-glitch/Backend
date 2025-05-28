import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from .models import Lay, DepositRotation, DepositAddress
from .serializers import LaySerializer

logger = logging.getLogger(__name__)

class AccountInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            active_lay = Lay.objects.filter(user=user, status='active')
            history = Lay.objects.filter(user=user, status='history')

            return Response({
                "balance": user.balance,
                "weekly_cashback": user.weekly_cashback,
                "active_lay": LaySerializer(active_lay, many=True).data,
                "history": LaySerializer(history, many=True).data
            })
        except Exception:
            return Response(
                {"detail": "Unexpected server error happend!"},
                status=500
            )

class GenerateDepositAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            with transaction.atomic():
                rotation = DepositRotation.objects.select_for_update().first()
                address = DepositAddress.objects.get(index=rotation.current_index)

                rotation.current_index = 1 if rotation.current_index == 10 else rotation.current_index + 1
                rotation.save()

            return Response({"address": address.address})
        except Exception as e:
            logger.exception("Error generating deposit address")
            return Response(
                {"detail": "Unexpected error has happend!"},
                status=500
            )
