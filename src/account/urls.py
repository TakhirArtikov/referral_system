from django.urls import path
from rest_framework import routers

from .views import (
    SignUpAPIView,
    SignInAPIView,
    ReferralByUserEmailAPIView,
    ReferralAPIView
)

app_name = 'account'
router = routers.DefaultRouter()
router.register(r'referrals', ReferralAPIView)

urlpatterns = [
    path('sign_up/', SignUpAPIView.as_view(), name='sign_up'),
    path('sign_in/', SignInAPIView.as_view(), name='sign_in'),
    path('user/<str:email>/referral/', ReferralByUserEmailAPIView.as_view(), name='referral_by_user_email'),
]

urlpatterns += router.urls
