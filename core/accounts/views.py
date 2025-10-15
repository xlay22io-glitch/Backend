import logging
from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from authentication.services import EmailService
from .models import Lay, DepositRotation, DepositAddress, WeeklyBonus
from .serializers import LaySerializer, WithdrawRequestSerializer, LayCreateSerializer, WeeklyBonusSerializer
from .utils import get_week_range


logger = logging.getLogger(__name__)


class AccountInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # try:
        user = request.user
        lays = Lay.objects.filter(user=user).order_by('-created_at')
        weekly_bonus = WeeklyBonus.objects.filter(user=user).last()

        return Response({
            "balance": user.balance,
            "weekly_cashback": user.weekly_cashback,
            "active_lay": LaySerializer(lays, many=True).data,
            "weekly_bonus": WeeklyBonusSerializer(weekly_bonus).data,
            "email": request.user.email
        })
        # except Exception:
        #     return Response(
        #         {"detail": "Unexpected server error happend!"},
        #         status=500
        #     )


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
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL]
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

        user = request.user
        data = serializer.validated_data

        with transaction.atomic():
            lay = Lay.objects.create(
                user=user,
                total_odds=data['total_odd'],
                stake_amount=data['stake_amount'],
                win_payout=data['win_payout'],
                file_name=data['file'].name,
                match=data['match'],
                tip=data['tip'],
                loss_payout=data['loss_payout'],
            )
            lay.file.save(data['file'].name, data['file'])
            lay.file_name = data['file'].name
            lay.save()

            user.balance -= data['stake_amount']
            user.save(update_fields=["balance"])

        logger.info(f"Lay created by {user.email}")

        try:
            send_mail(
                subject="New Lay Submission",
                message=f"User {user.email} submitted a lay with odds {data['total_odd']} and stake {data['stake_amount']}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(
                "Failed to send admin notification email for new lay")

        return Response({}, status=200)


class WeeklyBonusViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyBonusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeeklyBonus.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get or create current week’s record"""
        start, end = get_week_range()
        bonus, _ = WeeklyBonus.objects.get_or_create(
            user=request.user, week_start=start, week_end=end
        )
        bonus.calculate_reward()
        bonus.save()
        return Response(self.get_serializer(bonus).data)

    @action(detail=False, methods=["post"])
    def update_balance(self, request):
        """
        Admin logic: adjust weekly balance when OK/KO is clicked.
        Expected input: { "result": "ok", "amount": 0.5 }
        """
        start, end = get_week_range()
        bonus, _ = WeeklyBonus.objects.get_or_create(
            user=request.user, week_start=start, week_end=end
        )

        result = request.data.get("result")
        amount = float(request.data.get("amount", 0))

        if result == "ok":
            bonus.weekly_balance += amount  # Win payout
        elif result == "ko":
            bonus.weekly_balance -= amount  # Stake amount
        bonus.calculate_reward()
        bonus.save()
        return Response(self.get_serializer(bonus).data)


class DepositClickViewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            EmailService.notify_admin_email(
                subject="Deposit Clicked",
                message=f"User {request.user.email} clicked the copy deposit button.")

            return Response({"detail": "Deposity copy"}, status=200)
        except Exception as e:
            print(e)
            logger.exception("Error processing deposit click")
            return Response(
                {"detail": "Unexpected error has happend!"},
                status=500
            )
