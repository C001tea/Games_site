from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.http import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request: HttpRequest, sociallogin: SocialLogin, data):
        user = sociallogin.user
        if not user.pk:
            user.email = data.get("email")
        return user

    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin) -> None:
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
            saved_password = existing_user.password
            sociallogin.connect(request, existing_user)
            existing_user.refresh_from_db()
            if existing_user.has_usable_password() and saved_password and not saved_password.startswith("!"):
                existing_user.password = saved_password
                existing_user.save(update_fields=['password'])

        except User.DoesNotExist:
            pass

    def save_user(self, request: HttpRequest, sociallogin: SocialLogin, form=None):
        user = sociallogin.user
        if user.pk:
            saved_password = user.password
            result = super().save_user(request, sociallogin, form)
            if saved_password and not saved_password.startswith('!'):
                User.objects.filter(pk=user.pk).update(password=saved_password)
            return result
        return super().save_user(request, sociallogin, form)