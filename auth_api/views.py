import json
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


def _parse_json_body(request) -> Tuple[Optional[dict], Optional[JsonResponse]]:
    try:
        body = request.body.decode("utf-8") if request.body else "{}"
        return json.loads(body), None
    except json.JSONDecodeError:
        return None, JsonResponse({"message": "Invalid JSON body"}, status=400)


def _set_refresh_cookie(response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.AUTH_REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response) -> None:
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value="",
        max_age=0,
        httponly=True,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


def _authenticate_with_email_or_username(email: Optional[str], password: str):
    if not password:
        return None

    if email and "@" in email:
        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return None
        return authenticate(username=user.username, password=password)

    return authenticate(username=email, password=password)


@csrf_exempt
@require_POST
def login_view(request):
    data, error = _parse_json_body(request)
    if error:
        return error

    email = (data or {}).get("email") or (data or {}).get("username")
    password = (data or {}).get("password")
    if not email or not password:
        return JsonResponse({"auth_ok": False, "message": "Email and password required"}, status=400)

    user = _authenticate_with_email_or_username(email, password)
    if not user:
        return JsonResponse({"auth_ok": False, "message": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    response = JsonResponse(
        {
            "auth_ok": True,
            "message": "Login successful",
            "access_token": access_token,
        }
    )
    _set_refresh_cookie(response, str(refresh))
    return response


@csrf_exempt
@require_POST
def refresh_view(request):
    token_str = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if not token_str:
        return JsonResponse({"message": "Refresh token missing"}, status=401)

    try:
        old_refresh = RefreshToken(token_str)
    except TokenError:
        return JsonResponse({"message": "Refresh token invalid"}, status=401)

    user_id = old_refresh.get("user_id")
    if not user_id:
        return JsonResponse({"message": "Refresh token invalid"}, status=401)

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({"message": "User not found"}, status=401)

    new_refresh = RefreshToken.for_user(user)
    access_token = str(new_refresh.access_token)

    if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False):
        try:
            old_refresh.blacklist()
        except Exception:
            pass

    response = JsonResponse({"access_token": access_token})
    _set_refresh_cookie(response, str(new_refresh))
    return response


@csrf_exempt
@require_POST
def logout_view(request):
    response = JsonResponse({"message": "Logged out"})
    _clear_refresh_cookie(response)
    return response
