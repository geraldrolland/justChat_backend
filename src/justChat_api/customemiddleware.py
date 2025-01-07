import redis
from datetime import datetime
from django.http import HttpResponseForbidden, JsonResponse

from rest_framework import status

def IpLimiterMiddleware(get_response):
    def ip_limiter (request):
        r = redis.Redis()
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip:
            ip = ip.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        ip_rate_time = datetime.now()
        ip_addr = f"{ip}: rate per second{ip_rate_time.second}"
        num_of_req_in_1s = r.incrby(ip_addr, 1)
        if num_of_req_in_1s > 3:
             r.sadd("ip_blacklists", ip_addr)
             return JsonResponse({"error": "forbidden request"}, status=status.HTTP_403_FORBIDDEN)
        return get_response(request)
    return ip_limiter

"""
# myapp/middleware.py
import jwt
from .models import CustomUser
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async



@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return CustomUser.objects.get(id=user_id)
    except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
        return AnonymousUser()

async def JWTAuthMiddleware(inner):
    async def middleware(scope, receive, send):
        token = dict(scope["headers"]).get(b"authorization", b"").decode("utf-8")
        if token.startswith("Bearer "):
            token = token[7:]
        scope["user"] = await get_user_from_token(token)
        return await inner(scope, receive, send)
    return middleware


"""


from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
import jwt
from django.conf import settings
from .models import CustomUser

@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return CustomUser.objects.get(id=user_id)
    except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_params = scope.get("query_string").decode("utf-8")
        token = query_params.split("=")[1]
        scope["user"] = await get_user_from_token(token)
        return await self.inner(scope, receive, send)

