from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include, re_path 

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'google', GoogleAuthViewSet, basename='google')

urlpatterns = [
    path('', include(router.urls)),
    path('token-refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token-blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),
]