from django.conf import settings
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

from aventon.users.models import User, Profile

import jwt
from datetime import timedelta


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')


class UserLoginSerializer(serializers.Serializer):
    """User login serializer.

    Handle the login request data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=64)

    def validate(self, data):
        """Check credentials."""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_verified:
            raise serializers.ValidationError('Account is not active yet.')
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrive new token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class UserSignUpSerializer(serializers.Serializer):
    """User sign up serializer.

    Handle sign up data validation and user/profile creation.
    """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # Phone numer
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}',
        message="""Phone number must be entered in the format +999999999. Up to 15 digits allowed."""
    )
    phone_number = serializers.CharField(
        validators=[phone_regex],
        max_length=17,
    )

    password = serializers.CharField(min_length=6, max_length=64)
    password_confirmation = serializers.CharField(min_length=6, max_length=64)

    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        """Verify passwords math."""
        password = data['password']
        password_conf = data['password_confirmation']
        if password != password_conf:
            raise serializers.ValidationError("Passwords don't math.")
        password_validation.validate_password(password)
        return data

    def create(self, data):
        """Handle user and profile creation."""
        data.pop('password_confirmation')
        user = User.objects.create_user(**data, is_verified=False)
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        """Send account verication link to given user."""
        verification_token = self.gen_verification_token(user)
        subject = 'Welcome @{}! Verify your account to start ussing this app.'.format(user.username)
        from_email = 'Aventon <noreply@arnoldoricardo.com>'
        content = render_to_string('emails/users/account/verification.html',
                                   {'token': verification_token, 'user': user})
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, 'text/html')
        msg.send()

    def gen_verification_token(self, user):
        """Create JWT token that user can use to verify its account."""
        exp_data = timezone.now() + timedelta(days=3)
        payload = {
            'user': user.username,
            'exp': int(exp_data.timestamp()),
            'type': 'email_confirmation',
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token


class AccountVerificationSerializer(serializers.Serializer):
    """Account verification serializer."""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verify token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('verificaction link has expired.')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token.')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token.')

        print(payload)
        self.context['payload'] = payload

        return data

    def save(self):
        """Update user's verified status."""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.is_verified = True
        user.save()
