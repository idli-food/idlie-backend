from django.db.models import F
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coins


class AmountSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1, default=1)


class CoinsCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        coins, _ = Coins.objects.get_or_create(user=request.user)
        return Response({'count': coins.count})


class AddCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        Coins.objects.get_or_create(user=request.user)
        Coins.objects.filter(user=request.user).update(count=F('count') + amount)
        coins = Coins.objects.get(user=request.user)
        return Response({'count': coins.count})


class ReduceCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        Coins.objects.get_or_create(user=request.user)
        updated = Coins.objects.filter(user=request.user, count__gte=amount).update(count=F('count') - amount)
        coins = Coins.objects.get(user=request.user)
        if not updated:
            return Response(
                {'detail': 'Not enough coins.', 'count': coins.count},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'count': coins.count})
