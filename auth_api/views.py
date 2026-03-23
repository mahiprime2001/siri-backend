import json
from typing import Optional, Tuple

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

try:
    from supabase import create_client
except Exception:  # pragma: no cover - optional dependency for local dev
    create_client = None

_supabase_client = None


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


def _set_access_cookie(response, access_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=settings.AUTH_ACCESS_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.AUTH_ACCESS_COOKIE_SECURE,
        samesite=settings.AUTH_ACCESS_COOKIE_SAMESITE,
        path=settings.AUTH_ACCESS_COOKIE_PATH,
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


def _clear_access_cookie(response) -> None:
    response.set_cookie(
        key=settings.AUTH_ACCESS_COOKIE_NAME,
        value="",
        max_age=0,
        httponly=True,
        secure=settings.AUTH_ACCESS_COOKIE_SECURE,
        samesite=settings.AUTH_ACCESS_COOKIE_SAMESITE,
        path=settings.AUTH_ACCESS_COOKIE_PATH,
    )


def _get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not create_client:
        return None

    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        return None

    _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase_client


def _authenticate_with_supabase(supabase, email: str, password: str):
    if not email or not password:
        return None
    response = supabase.table("users").select("*").eq("email", email).execute()
    if not response.data:
        return None

    user = response.data[0]
    stored_password = user.get("password", "")
    if stored_password != password:
        return None

    return user


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
    email = str(email).strip().lower()

    supabase = _get_supabase_client()
    if not supabase:
        return JsonResponse(
            {"auth_ok": False, "message": "Supabase not configured or unavailable"},
            status=503,
        )

    try:
        user = _authenticate_with_supabase(supabase, email, password)
    except Exception:
        return JsonResponse(
            {"auth_ok": False, "message": "Supabase unavailable. Try again."},
            status=503,
        )
    if not user:
        return JsonResponse({"auth_ok": False, "message": "Invalid credentials"}, status=401)

    user_id = str(user.get("id") or "")
    refresh = RefreshToken()
    refresh["user_id"] = user_id
    refresh["email"] = user.get("email", email)
    refresh["name"] = user.get("name", "Unknown")
    refresh["role"] = user.get("role", "user")

    access_token = str(refresh.access_token)

    response = JsonResponse(
        {
            "auth_ok": True,
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user_id,
                "email": user.get("email", email),
                "name": user.get("name", "Unknown"),
            },
            "user_role": user.get("role", "user"),
        }
    )
    _set_refresh_cookie(response, str(refresh))
    _set_access_cookie(response, access_token)
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

    new_refresh = RefreshToken()
    new_refresh["user_id"] = user_id
    if "email" in old_refresh:
        new_refresh["email"] = old_refresh["email"]
    if "name" in old_refresh:
        new_refresh["name"] = old_refresh["name"]
    if "role" in old_refresh:
        new_refresh["role"] = old_refresh["role"]

    access_token = str(new_refresh.access_token)

    if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False):
        try:
            old_refresh.blacklist()
        except Exception:
            pass

    response = JsonResponse({"access_token": access_token})
    _set_refresh_cookie(response, str(new_refresh))
    _set_access_cookie(response, access_token)
    return response


@csrf_exempt
@require_POST
def logout_view(request):
    response = JsonResponse({"message": "Logged out"})
    _clear_refresh_cookie(response)
    _clear_access_cookie(response)
    return response


def health_view(request):
    return JsonResponse({"status": "ok"})
