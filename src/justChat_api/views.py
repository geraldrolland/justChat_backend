from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.cache  import cache_page, never_cache, cache_control
from django.core.cache import cache
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from .serializer import *
from .custompermissions import *
import random
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
import requests
import base64
import uuid
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from .services import get_user_data
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login
from rest_framework.views import APIView
from .serializer import AuthSerializer
from django.db.models import Q
from .format_date import FormatDate
from django.core.cache import cache
from .tasks import send_user_otp
channel_layer = get_channel_layer()
#from .formatdate import FormatDate
# Create your views here.


class UserViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def create_user(self, request):
        """

        This endpoint create user with a valid and verified credentials

        Args:
            self (object): the instance of the class
            request (dict): a dictionary containing the request body
        
        Returns:
            Response: the credentials of user

        """
        if cache.get(request.data.get("email"), default=None) is not None:
            email_verified = json.loads(cache.get(request.data.get("email")))
            if email_verified.get("is_email_verified") == True:
                user_password = request.data.pop("password")
                request.data.update(email_verified)
                cache.delete(request.data.get("email"))
                user = CustomUser.objects.create(**request.data)
                user.set_password(user_password)
                user.is_online = True
                user.save()
                refresh = RefreshToken.for_user(user=user)
                return Response({
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "profile_image": user.profile_image if user.profile_image else None,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),

                }, status=status.HTTP_201_CREATED)
            return Response({"error": "permission denied invalid or unverified email"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], permission_classes=[AllowAny], )
    def verify_email(self, request):
        """

        This endpoint validate the verify the user email through a two factor authentication

        Args:
            self (object): instance of the class
            request (object): a request that contains the body of request

        Returns:
            Response: 200 status code

        Raises:
            Bad Request: 400 status code 

        """
        try:
            CustomUser.objects.get(email=request.data.get("email"))
            return Response({"error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist as e:
            otp = random.randint(51011, 89630)
            print("this is the code", otp)
            cache.set(request.data.get("email"), value=otp, timeout=120)
            subject = "User Email Verification"
            html_content = f'''
                <html><body> 
                <div>Dear Sir / Madam,</div>
                <div>To verify your email, use this OTP:</div>
                <span>{otp}</span>
                <div>This OTP is valid for the next 2 minutes. Do not share it.</div>
                <div>Thank you for using justChat.com.</div>
                <div>Best regards,<br>justChat Support Team</div>
                </body></html>
            '''
            mail_from = settings.EMAIL_HOST_USER
            recipient = [request.data.get("email")]
            send_user_otp(subject, html_content, mail_from, recipient)
            print(f"this is the first endpoint otp {cache.get(request.data.get("email"))}")
            return Response({"detail": "OTP created successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def verify_otp(self, request):
        """

        This endpoint verifies the otp code submitted using a post request

        Args:
            self (object): This parameter is the  instance of the class
            request (object): This parameter is request and contains  data about the request
        
        Returns:
            Response: request accepted with 200 status code

        Raises:
            Not Acceptable: 406 status code, request not accepted 

        """
        otp_code = str(request.data.get("otpCode"))
        print("this is the second end point", cache.get(request.data.get("email"))) 
        if otp_code and otp_code == str(cache.get(request.data.get("email"), default=None)):
            cache.set(request.data.get("email"), json.dumps({"is_email_verified": True}))
            response = Response({"detail": "OTP verified successfully"}, status=status.HTTP_200_OK)
            return response
        return Response({"detail": "Invalid OTP"}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login_user(self, request):
        """

        This end point logs in a user with a valid credential and returns 
        user credentails including a refresh and access token for JWT authentication

        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contains data about the request
        
        Returns:
            Response: request accepted with a status code of 200
        
        Raises:
            Bad Request: bad request with a status code of 400

        """
        user = get_object_or_404(CustomUser, email=request.data.get("email"))

        if user.check_password(request.data.get("password")):
            user.is_online = True
            user.save()
            refresh = RefreshToken.for_user(user=user)
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_image": user.profile_image if user.profile_image else None,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["get"])

    def add_a_friend(self, request, pk=None):
        """

        This endpoint allows user to add friend using the provided id in the url

        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contain data about the request
            pk (int | str): this paramter is the contain the user's friend id
        
        Returns:
            Response: request accepted with status code 200
        
        Raises:
            Not Found: not found with a status code of 404
        """
        friend = get_object_or_404(CustomUser, id=pk)
        user = get_object_or_404(CustomUser, email=request.user.get("email"))
        user.friends.add(friend)
        user.save()
        return Response({"detail": "friend added successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=False, permission_classes=[IsAuthenticated], authentication_classes=[SessionAuthentication, JWTAuthentication, BasicAuthentication], methods=["post"])
    def create_group(self, request):
        """

        This endpoint allows the user to create a group

        Args:
            self (object): this paramter is the instance of the class
            request (object): this paramter is the request object and contains data about the request
        
        Returns:
            Response: resource created with a status code of 201

        """
        print('THIS IS THE GROUP NAME', request.data.get("name"))
        group = {
            "group_name": request.data.get("name"),
            "group_photo": request.data.get("image"),
            "author": request.user,
        }
        group = Group.objects.create(**group)
        group.participants.add(request.user)
        for participant in request.data.get("participants"):
            participant = CustomUser.objects.get(id=participant.get("id"))
            is_group_admin_obj = {
                "group": group,
                "user": participant,
            }
            is_group_admin_obj = IsGroupAdmin.objects.create(**is_group_admin_obj)
            is_group_admin_obj.save()
            group.participants.add(participant)
        group.save()
        is_group_admin_obj = {
            "group": group,
            "IsGroupAdmin": True,
            "user": request.user,
        }
        is_group_admin_obj = IsGroupAdmin.objects.create(**is_group_admin_obj)
        is_group_admin_obj.save()
        return Response({
            "group_id": group.group_id,
            "name": group.group_name,
            "group_photo": group.group_photo,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["post"])
    def add_friend_to_group(self, request, pk=None):
        """

        This endpoint allows user to add a friend to group

        Args:
            self (object): this paramter is the instance of the class
            request (object): this paramter is the request object and contains data about the request
            pk (int | str): this paramter contains the id of the group
        Returns:
            Response: resource created successfully with a status of 201
        
        Raises:
            Not Found: resource not found with status of code of 404

        """
        group = get_object_or_404(Group, group_id=pk)
        for friend in request.data:
            friend = get_object_or_404(CustomUser, id=friend[id])
            try:
                IsGroupAdmin.objects.filter(user=friend.id, group=group.group_id)
                continue
            except IsGroupAdmin.DoesNotExist as e:
                is_group_admin_obj = {
                "group": group.group_id,
                "user": friend.id,
                }
                is_group_admin_obj = IsGroupAdmin.objects.create(**is_group_admin_obj)
                is_group_admin_obj.save()
                group.participants.add(friend)
            group.save()
        return Response({"detail": "friends added to group successfully"}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], permission_classes=[IsAuthenticated], methods=["get"])
    def user_exit_group(self, request, pk=None):
        """

        This endpoint allow user to exist a group

        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contains data about the request
            pk (int | str): this paramter contain the id of the group
        
        Return:
            Response: request accepted with a status code of 200
        
        Raises:
            Not Found: resource not found with a status code of 404

        """
        group = get_object_or_404(Group, group_id=pk)
        is_group_admin = IsGroupAdmin.objects.get(group=group.group_id, user=request.user.id)
        is_group_admin.delete()
        is_group_admin.save()
        group.participants.remove(request.user)
        group.save()
        return Response({"detail": "exited group succcesfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], permission_classes=[IsAuthenticated], methods=["post"])
    def make_friend_group_admin(self, request, pk=None):
        """

        This endpoint allow user with group admin privilege to grant friend group admin privilege

        Args:
            self (object): this paramter is the instance of the class
            request (object): this paramter is the request object and contains data about the request
            pk (int | str): this parameter contains the id of the group

        Return:
            Response: request accepted with a status code 200

        Raises:
            Not Found: resource not found with a status code 
            Permission Denied: permission denied with a status code of 403 

        """
        friend = get_object_or_404(CustomUser, id=request.data.get("id"))
        group = get_object_or_404(Group, group_id=pk)
        try:
            is_group_admin = IsGroupAdmin.objects(group=group.group_id, user=request.user.id)
            if is_group_admin.IsGroupAdmin == True:
                is_group_admin = IsGroupAdmin.objects.get(group=group.group_id, user=friend.id)
                if is_group_admin.IsGroupAdmin != True:
                    is_group_admin.IsGroupAdmin = True
                is_group_admin.save()
                return Response({"detail": "grant friend group admin privileges succefully"}, status=status.HTTP_200_OK)
            return Response({"error": "permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except IsGroupAdmin.DoesNotExist as e:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[SessionAuthentication, BasicAuthentication, JWTAuthentication], methods=["post"])
    def revoke_friend_group_admin(self, request, pk=None):
        """

        This endpoint allow user with group admin privilege to revoke friend group admin privilege

        Args:
            self (object): this paramter is the instance of the class
            request (object): this paramter is the request object and contains data about the request
            pk (int | str): this parameter contains the id of the group

        Return:
            Response: request accepted with a status code 200

        Raises:
            Not Found: resource not found with a status code 
            Permission Denied: permission denied with a status code of 403 

        """
        friend = get_object_or_404(CustomUser, id=request.data.get("id"))
        group = get_object_or_404(Group, group_id=pk)
        try:
            is_group_admin = IsGroupAdmin.objects(group=group.group_id, user=request.user.id)
            if is_group_admin.IsGroupAdmin == True:
                is_group_admin = IsGroupAdmin.objects.get(group=group.group_id, user=friend.id)
                if is_group_admin.IsGroupAdmin != False:
                    is_group_admin.IsGroupAdmin = False
                is_group_admin.save()
                return Response({"detail": "revoked friend group admin privileges succefully"}, status=status.HTTP_200_OK)
            return Response({"error": "permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except IsGroupAdmin.DoesNotExist as e:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["get"])
    def get_group_participant(self, request, pk=None):
        """

        This end point retreives all participants in a group

        Args:
            self (object): this paramter is the instance of the class
            request (object): this parameter is the request object and contains the request data
            pk (str | int): this paramter is the id of group
        
        Return:
            Response: the list of participant with status code 200
        
        Raises:
            Not Found: not found with a status code 404

        """
        group = get_object_or_404(Group, group_id=pk)
        if group.participants.all():
            participant_list = []
            for participant in group.participants.all():
                is_group_admin = Group.objects.get(group=group.group_id, user=participant.id)
                participant_obj = {
                    "id": participant.id,
                    "username": participant.username,
                    "profile_image": participant.profile_image if participant.profile_image else None,
                    "is_group_admin": is_group_admin.IsGroupAdmin,
                }
                participant_list.append(participant_obj)
            return Response(participant_list, status=status.HTTP_200_OK)
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication])
    def get_friends(self, request):
        """

        This end point retrieves users friends and their last recorded message

        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contains data about the request
        
        Returns:
            Response: returns a list of users friends with a status code of 200
        
        Raises:
            Not Found: resource not found with status code of 404

        """
        user = get_object_or_404(CustomUser, email=request.user.email)
        user_friends = CustomUser.objects.all().exclude(id=user.id) #user.friends.all()
        if user_friends:
            friend_list = []
            for friend in user_friends:
                user_and_friend_msg = Message.objects.filter(Q(sender=user.id, receipient=friend.id) | Q(sender=friend.id, receipient=user.id)).order_by("created_at")
                user_and_friend_last_msg = user_and_friend_msg[len(user_and_friend_msg) - 1] if user_and_friend_msg else None
                friend_obj = {
                    "id": friend.id,
                    "username": friend.username,
                    "profile_image": friend.profile_image if friend.profile_image else None,
                    "is_online": friend.is_online,
                    "last_date_online": FormatDate.format_date(friend.last_date_online) if friend.last_date_online else None,
                    "last_message":  {
                        "message_id": user_and_friend_last_msg.message_id,
                        "sender_username": user_and_friend_last_msg.sender.username,
                        "sender_id": user_and_friend_last_msg.sender.id,
                        "image": user_and_friend_last_msg.image if user_and_friend_last_msg.image else None,
                        "video": user_and_friend_last_msg.video if user_and_friend_last_msg.video else None,
                        "audio": user_and_friend_last_msg.audio if user_and_friend_last_msg.audio else None,
                        "text": user_and_friend_last_msg.text if user_and_friend_last_msg.text else None,
                        "created_at": FormatDate.format_date(user_and_friend_last_msg.created_at),
                        "is_receipient_online": user_and_friend_last_msg.is_receipient_online
                    } if user_and_friend_last_msg is not None else None
                }
                friend_list.append(friend_obj)
            return Response(friend_list, status=status.HTTP_200_OK)
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["get"], permission_classes=[IsAuthenticated])
    def get_groups(self, request):
        """

        This end point retrieves users groups

        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contains the data obout the request
        
        Return:
            Response: returns the list of users group with a status code of 200
        
        Raises:
            Not Found: resource not found with a status code of 404

        """
        user = get_object_or_404(CustomUser, email=request.user.email)
        user_groups = user.all_groups.all()
        if user_groups:
            group_list = []
            for group in user_groups:
                group_messages = Message.objects.filter(group=group.group_id).order_by("created_at")
                if len(group_messages) != 0:
                    size = len(group_messages)
                    last_group_msg = group_messages[size - 1]
                else:
                    last_group_msg = None
                group_obj = {
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "group_photo":  group.group_photo if group.group_photo else None,
                    "last_message": {
                        "message_id": last_group_msg.message_id,
                        "video": last_group_msg.video if last_group_msg.video else None,
                        "image": last_group_msg.image if last_group_msg.image else None,
                        "audio": last_group_msg.audio if last_group_msg.audio else None,
                        "text": last_group_msg.text if last_group_msg.text else None,
                        "sender_username": last_group_msg.sender.username,
                        "sender_id": last_group_msg.sender.id,
                        "created_at": FormatDate.format_date(last_group_msg.created_at)
                    } if last_group_msg else None
                }
                group_list.append(group_obj)
            return Response(group_list, status=status.HTTP_200_OK)
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["post"])
    def send_message_to_group(self, request, pk=None):
        group = get_object_or_404(Group, group_id=pk)
        sender = get_object_or_404(CustomUser, email=request.user.email)
        request.data["sender"] = sender
        request.data['group'] = group
        request.data["receipient"] = None
        request.data['created_at'] = datetime.strptime(request.data.get("created_at"), '%m/%d/%Y, %I:%M:%S %p')
        message = Message.objects.create(**request.data)
        message.save()
        print("THE MESSAGE SAVED")
        group_msg_obj = {
            "message_id": message.message_id,
            "video": message.video if message.video else None,
            "audio": message.audio if message.audio else None,
            "image": message.image if message.image else None,
            "text": message.text if message.text else None,
            "group": group.group_id,
            "created_at": FormatDate.format_date(message.created_at),
            "sender": {
                "id": message.sender.id,
                "username": message.sender.username,
                "profile_image": message.sender.profile_image if message.sender.profile_image else None
                }
        }
        async_to_sync(channel_layer.group_send)(group.group_name.replace(" ", "_"), {
            "type": "send.message.to.group",
            "message": group_msg_obj,
        })

        return Response(group_msg_obj, status=status.HTTP_200_OK)

    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["post"])
    def send_message_to_friend(self, request, pk=None):
        """
        This endpoint allows user to send message to friend
        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contains the data about the request
            pk (int | str): this paramter is the id of the friend
        Return:
            Response: request accepted with a status code of 200
        Raises:
            Not Found: resource not found with a status code of 404

        """

        friend = get_object_or_404(CustomUser, id=pk)
        user = get_object_or_404(CustomUser, email=request.user.email)
        message = request.data
        message["created_at"] = datetime.strptime(message.get("created_at"), '%m/%d/%Y, %I:%M:%S %p')
        print(f'THIS IS THE MESSAGE SENT {message}')
        message["sender"] = user
        message["receipient"] = friend
        message_obj = Message.objects.create(**message)
        friend_channel_name = cache.get(friend.id, default=None)
        if friend_channel_name is not None:
            if friend.is_online:
                message_obj.is_receipient_online = True
            message.update({"message_id":message_obj.message_id, "created_at": FormatDate.format_date(message_obj.created_at), "is_receipient_online": message_obj.is_receipient_online})
            message_obj.save()
            print("MESSAGE IS ONLINE", message["is_receipient_online"])
            message["sender"] = user.id
            message["receipient"] = friend.id
            async_to_sync(channel_layer.send)(friend_channel_name,{
                "type": "send.message.to.friend",
                "message": message
            })
        else:
            message.update({"message_id":message_obj.message_id, "created_at": FormatDate.format_date(message_obj.created_at), "is_receipient_online": message_obj.is_receipient_online})
            message_obj.save()
        message["sender"] = user.id
        message["receipient"] = friend.id
        print(type(message))
        return Response(message, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, BasicAuthentication, SessionAuthentication])
    def get_user_and_frnd_msgs(self, request, pk=None):
        """
        THis endpoint retrieves user and friend messages

        Args:
            self (object): this parameter is the instance of the class
            request (object): this parameter is the request object and contains the the request data
            pk: this parameter is the user's friend id
        
        Return:
            Response: returns a list  of message dictionary with a status code of 200

        Raises:
            Not Found: resource not found with status code of 404

        """
        friend = get_object_or_404(CustomUser, id=pk)
        user = get_object_or_404(CustomUser, email=request.user.email)
        messages = Message.objects.filter(Q(sender=friend.id, receipient=user.id) | Q(sender=user.id, receipient=friend.id)).order_by("created_at")
        if messages:
            message_list = []
            for message in messages:
                if message.receipient.id == user.id:
                    if message.is_receipient_online == False:
                        message.is_receipient_online = True
                        message.save()
                message_obj = {
                    "message_id": message.message_id,
                    "image": message.image if message.image else None,
                    "video": message.video if message.video else None,
                    "audio": message.audio if message.audio else None,
                    "text": message.text if message.text else None,
                    "file": message.file if message.file else None,
                    "sender": message.sender.id,
                    "receipient": message.receipient.id,
                    "is_receipient_online": message.is_receipient_online,
                    "created_at": FormatDate.format_date(message.created_at)
                }
                message_list.append(message_obj)
            return Response(message_list, status=status.HTTP_200_OK)
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, permission_classes=[IsAuthenticated], authentication_classes=[JWTAuthentication, SessionAuthentication, BasicAuthentication], methods=["get"])
    def get_user_and_group_msgs(self, request, pk=None):
        """
        This endpoint retrieves user and group messages

        Args:
            self (obejct): this is the instance of the class
            request (object): this parameter is the request object and contains the data of the request
            pk (int | str): this paramter is the id of the group
        
        
        Return:
            Response: returns a list of dictionary of messages with a status code of 200
        
        Raises:
            Not Found: resource not found with a status code of 404
        """
        group = get_object_or_404(Group, group_id=pk)
        group_messages = group.messages.all().order_by('created_at')
        if group_messages:
            group_message_list = []
            for group_msg in group_messages:
                group_msg_obj = {
                    "message_id": group_msg.message_id,
                    "video": group_msg.video if group_msg.video else None,
                    "audio": group_msg.audio if group_msg.audio else None,
                    "image": group_msg.image if group_msg.image else None,
                    "text": group_msg.text if group_msg.text else None,
                    "group": group.group_id,
                    "created_at": FormatDate.format_date(group_msg.created_at),
                    "sender": {
                        "id": group_msg.sender.id,
                        "username": group_msg.sender.username,
                        "profile_image": group_msg.sender.profile_image if group_msg.sender.profile_image else None
                    }
                }

                group_message_list.append(group_msg_obj)
            return Response(group_message_list, status=status.HTTP_200_OK)
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, permission_classes=[IsAuthenticated], authentication_classes=[BasicAuthentication, JWTAuthentication, SessionAuthentication], methods=["post"])
    def logout_user(self, request):
        user = get_object_or_404(CustomUser, email=request.user.email)
        user.channel_name = None
        user.last_date_online = datetime.now().isoformat()
        user.is_online = False
        user.save()
        print("logged out")
        return Response({"detail": "logged out succesfully"}, status=status.HTTP_200_OK)


    @action(detail=False, permission_classes=[AllowAny], methods=["get"])
    def check_limit(self, request):
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)
    
    @staticmethod
    def otp_hash_algo(otp):
        otp_str = str(otp)
        hash_map_dict = {
        '0': '}?<%', '1': '*\\)>',
        '2': '/$<?', '3': '/($?',
        '4': '!$@<', '5': ']..$',
        '6': '@){:', '7': ']:,$', 
        '8': '],)/', '9': '>*!&'
        }
        hash_str = ""
        i = 0
        for ch in otp_str:
            hash_str += hash_map_dict[ch]
            if i != 3:
                hash_str += "="
            i += 1
        return hash_str
    
    @staticmethod
    def otp_unhash_algo(hash_str):
        if hash_str is None:
            print("hash_str is none")
        print(hash_str)
        unhash_map_dict = {
            '}?<%': "0", '*\\)>': "1",
            '/$<?': "2", '/($?': "3",
            '!$@<': "4", ']..$': "5",
            '@){:': "6", ']:,$': "7",
            '],)/': "8", '>*!&': "9"
        }
        otp_str = ""
        hash_str = hash_str.split("=")
        print("this is the hash str list", hash_str)
        for _str in hash_str:
            otp_str += unhash_map_dict[_str]
        return otp_str
    


class GoogleAuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def google_login(self, request):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        validated_data = auth_serializer.validated_data
        user_data = get_user_data(validated_data)
        try:
            user = CustomUser.objects.get(email=user_data['email'])
            refresh = RefreshToken.for_user(user=user)
            return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
        except KeyError as e:
            return redirect("http://localhost:5173/log-in")