from datetime import datetime
from .format_date import FormatDate
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from .models import *
from django.shortcuts import  get_object_or_404
from  .serializer import *
from channels.db import database_sync_to_async
import jwt
from django.core.cache import cache
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        try:   
            token = self.scope['query_string'].decode("utf-8").split("=")[1]
            user = await database_sync_to_async(jwt.decode)(token, settings.SECRET_KEY, algorithms=["HS256"])
            await self.accept()
            self.user = await database_sync_to_async(CustomUser.objects.get)(id=user.get("user_id"))
            self.user.channel_name = self.channel_name
            cache.set(self.user.id, self.channel_name)

        except (jwt.ExpiredSignatureError, KeyError, jwt.DecodeError, CustomUser.DoesNotExist):
            await self.close(code=1006)

    async def receive(self, text_data=None):
        message = json.loads(text_data)
        if message["isTyping"] == True:
            try:
                friend_channel_name = cache.get(message["receipient"], default=None)
                if friend_channel_name is not None:
                    await self.channel_layer.send(
                        friend_channel_name, {
                            "type": "send.message.to.friend",
                            "message": message,
                        }
                    )
            except KeyError:
                pass
    
    async def send_message_to_friend(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        if self.user:
            cache.delete(self.user.id)
        await self.close()
        


class IsUserOnlineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:   
            token = self.scope['query_string'].decode("utf-8").split("=")[1]
            self.user = await database_sync_to_async(jwt.decode)(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(f"connected user {self.user.get('user_id')}")
            await self.accept()
        except (jwt.ExpiredSignatureError, KeyError, jwt.DecodeError, CustomUser.DoesNotExist):
            await self.close(code=1006)
    

    async def disconnect(self, code):
        print(f"disconected user {self.user.get('user_id')}")
        await self.close()

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        try:   
            token = self.scope['query_string'].decode("utf-8").split("=")[1]
            await database_sync_to_async(jwt.decode)(token, settings.SECRET_KEY, algorithms=["HS256"])
            await self.accept()
            group_id = self.scope['url_route']['kwargs']['group_id']
            self.group = await database_sync_to_async(Group.objects.get)(group_id=group_id)
            self.group.group_name = self.group.group_name.replace(" ", "_")
            await self.channel_layer.group_add(
                self.group.group_name,
                self.channel_name,
            )
            cache.set(self.channel_name, self.group.group_name)

        except (jwt.ExpiredSignatureError, KeyError, jwt.DecodeError, CustomUser.DoesNotExist):
            await self.close(code=1006)

    async def receive(self, text_data=None):
        message = json.loads(text_data)
        if message["isTyping"] == True:
            await self.channel_layer.group_send(
                self.group.group_name, {
                    "type": "send.message.to.group",
                    "message": message,
                    }
                )
    
    async def send_message_to_group(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def disconnect(self, code):
        group_name = cache.get(self.channel_name, default=None)
        if group_name:
            await self.channel_layer.group_discard(
                self.group.group_name,
                self.channel_name,
                )
        await self.close()


class VideoCallConsumer(AsyncWebsocketConsumer):
    pass




