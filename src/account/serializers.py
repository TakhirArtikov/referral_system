from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed

from account.hunter_client import hunter_client
from account.models import User, Referral


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    referral_code = serializers.CharField(
        write_only=True, required=False,
        min_length=Referral.CODE_LENGTH, max_length=Referral.CODE_LENGTH
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'referral_code', 'password', 'password2')

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('password2'):
            raise serializers.ValidationError({'password': _('Passwords must match')})

        attrs['username'] = attrs['email']
        if attrs.get("referral_code"):
            try:
                referral = Referral.objects.get(code=attrs.pop("referral_code"))
                if not referral.is_active:
                    raise serializers.ValidationError(
                        {"referral_code": f"Referral code is inactive: {attrs.get('referral_code')}"}
                    )
                attrs["referral"] = referral
            except Referral.DoesNotExist:
                raise serializers.ValidationError(
                    {"referral_code": f"Invalid referral_code: {attrs.get('referral_code')}"})

        if not hunter_client.verify_email(attrs['email']):
            raise serializers.ValidationError({'email': "Invalid email"})

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'tokens')

    @staticmethod
    def get_tokens(data):
        return User.objects.get(email=data['email']).tokens()

    def validate(self, attrs):
        user = auth.authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise AuthenticationFailed(_('Invalid credentials, try again'))
        if not user.is_active:
            raise AuthenticationFailed(_('Account disabled, contact admin'))
        return attrs


class ReferralCodeByUserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ('id', 'code',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')


class ReferralSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )

    class Meta:
        model = Referral
        fields = ('id', 'code', 'expiration_date', 'is_active', 'user')

    def validate(self, attrs):
        expiration_date = attrs.get('expiration_date')
        if expiration_date < timezone.now().date():
            raise serializers.ValidationError({'expiration_date': 'Please select correct date for expiration'})

        return attrs
