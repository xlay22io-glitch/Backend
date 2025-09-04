import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from django.core.mail import send_mail

from .models import Lay, DepositRotation, DepositAddress
from .serializers import LaySerializer, WithdrawRequestSerializer, LayCreateSerializer

logger = logging.getLogger(__name__)


class AccountInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            lays = Lay.objects.filter(user=user)

            return Response({
                "balance": user.balance,
                "weekly_cashback": user.weekly_cashback,
                "active_lay": LaySerializer(lays, many=True).data,

                "email": request.user.email
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
                address = DepositAddress.objects.get(
                    index=rotation.current_index)
                max_index = (
                    DepositAddress.objects.order_by('-index')
                    .values_list('index', flat=True)
                    .first()
                )
                rotation.current_index = 1 if rotation.current_index >= max_index else rotation.current_index + 1

                rotation.save()

            return Response({"address": address.address})
        except Exception as e:
            logger.exception("Error generating deposit address")
            return Response(
                {"detail": "Unexpected error has happend!"},
                status=500
            )


class WithdrawRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = WithdrawRequestSerializer(
                data=request.data, context={'request': request})
            if not serializer.is_valid():
                errors = serializer.errors
                if "amount" in errors:
                    return Response({"detail": errors["amount"][0]}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"detail": "Data is not valid!"}, status=status.HTTP_400_BAD_REQUEST)

            withdraw_request = serializer.save(user=request.user)

            logger.info(
                f"Withdraw requested by user {request.user.email} for amount {withdraw_request.amount}")

            send_mail(
                subject="New Withdraw Request",
                message=f"User {request.user.email} requested withdrawal of {withdraw_request.amount} to address {withdraw_request.address}.",
                from_email="noreply@tradelayback.com",
                recipient_list=["admin@tradelayback.com"]
            )

            return Response({"detail": "We received your request! We will get back to you shortly!"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Withdraw request failed")
            return Response({"detail": "Internal Server Error!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalculatorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LayCreateSerializer(
            data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.warning(f"Invalid data: {serializer.errors}")
            return Response({"detail": serializer.errors}, status=400)

        try:
            user = request.user
            data = serializer.validated_data

            with transaction.atomic():
                lay = Lay.objects.create(
                    user=user,
                    total_odds=data['total_odd'],
                    stake_amount=data['stake_amount'],
                    win_payout=data['win_payout'],
                    file_name=data['file'].name,
                    status="active",
                    match=data['match'],
                    tip=data['tip'],
                    loss_payout=data['loss_payout']
                )

                lay.file.save(data['file'].name, data['file'])
                lay.file_name = data['file'].name
                lay.save()

                user.balance -= data['stake_amount']
                user.save()

            logger.info(f"Lay created by {user.email}")

            send_mail(
                subject="New Lay Submission",
                message=f"User {user.email} submitted a lay with odds {data['total_odd']} and stake {data['stake_amount']}.",
                from_email="noreply@tradelayback.com",
                recipient_list=["admin@tradelayback.com"]
            )

            return Response({}, status=200)

        except Exception as e:
            logger.exception("Lay submission failed")
            return Response({"detail": "Internal Server Error!"}, status=500)
