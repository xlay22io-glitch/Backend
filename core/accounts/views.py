from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Lay
from .serializers import LaySerializer

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
