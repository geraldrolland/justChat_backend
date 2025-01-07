from django.urls import re_path, path
from . import consumer


websocket_urlpatterns = [
  path('ws/groupchat/<str:group_id>/', consumer.GroupChatConsumer.as_asgi()),
  path('ws/chat/<str:friend_id>/', consumer.ChatConsumer.as_asgi()),
  path('ws/isuseronline/', consumer.IsUserOnlineConsumer.as_asgi()),

]