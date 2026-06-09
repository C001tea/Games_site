from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm
from .models import User
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f'https://game-vault.dev/accounts/verify/{uid}/{token}/'
            # link = f'http://127.0.0.1:8000/accounts/verify/{uid}/{token}/'
            send_mail(
                subject="Verify email",
                message=f"To verify email follow the link: {link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return render(request, 'accounts/check_email.html')

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {"form": form})

@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return render(request, 'accounts/invalid_link.html')

def ratelimit_blocked(request, exception=None):
    return render(request, 'accounts/ratelimit.html', status=429)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)

            return redirect('home')
        else:
            error = "Invalid login or password."
            try:
                existing_user = User.objects.get(email=email)
                if not existing_user.has_usable_password():
                    error = "This account uses Google login. Please sign in with Google."
            except User.DoesNotExist:
                pass
            return render(request, 'accounts/login.html', {"error": error})

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')