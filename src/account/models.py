import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    email = models.EmailField(_("Email address"), unique=True)
    referral = models.ForeignKey(
        verbose_name=_("Registered referral code"), to="Referral",
        on_delete=models.SET_NULL, related_name="registered_users",
        null=True, blank=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email

    def tokens(self) -> Dict[str, str]:
        """
            Get token by current user
        :return: Token
        :rtype Dict[str, str]
        """
        refresh = RefreshToken.for_user(user=self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class Referral(models.Model):
    CODE_LENGTH = 8

    user = models.ForeignKey(
        verbose_name=_("User"), to=User,
        on_delete=models.CASCADE, related_name="referrals"
    )
    code = models.CharField(verbose_name=_("Code"), blank=True, unique=True, max_length=CODE_LENGTH)
    expiration_date = models.DateField(_("Expiration date"))
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Referral")
        verbose_name_plural = _("Referrals")

    def __str__(self):
        return f'{self.user} - {self.code}'

    @classmethod
    def generate_referral_code(cls) -> str:
        new_code = get_random_string(length=cls.CODE_LENGTH)

        # WARNING: N + 1 problem
        while cls.objects.filter(code=new_code).exists():
            new_code = get_random_string(length=cls.CODE_LENGTH)

        return new_code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Referral.generate_referral_code()
        super().save(*args, **kwargs)
