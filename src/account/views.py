from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from account.models import User, Referral
from account.serializers import (
    SignUpSerializer,
    SignInSerializer,
    ReferralCodeByUserEmailSerializer,
    ReferralSerializer
)


class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


class SignInAPIView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = SignInSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralByUserEmailAPIView(generics.GenericAPIView):
    queryset = Referral.objects.filter(is_active=True)
    serializer_class = ReferralCodeByUserEmailSerializer

    def get(self, request, email, *args, **kwargs):
        referral = get_object_or_404(Referral, user__email=email)
        serializer = self.get_serializer(referral)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ReferralAPIView(ModelViewSet):
    queryset = Referral.objects.select_related('user').order_by('-id')
    serializer_class = ReferralSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
