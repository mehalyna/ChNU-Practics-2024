from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
import jwt
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


def send_email(subject: str, message: str, recipient_list: list[str]) -> None:
    if (
        settings.EMAIL_HOST_USER
        and settings.EMAIL_HOST_PASSWORD
        and len(recipient_list) > 0
    ):
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


def get_verification_link(request, user, verify_path: str) -> str:
    domain = get_current_site(request).domain
    token = RefreshToken.for_user(user)
    access_token = str(token.access_token)
    return f"http://{domain}{verify_path}?token={access_token}"


def send_confirmation_email(request, user):
    verify_email_path = reverse("verify-email")
    link = get_verification_link(request, user, verify_email_path)
    send_email(
        "Verify your email address",
        f"Click the link to verify your email address: {link}",
        [user.email],
    )


def get_user_from_token(token):
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=settings.SIMPLE_JWT["ALGORITHM"]
    )
    return User.objects.get(id=payload["user_id"])
