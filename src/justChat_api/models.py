from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timezone, datetime
from .customusermanager import CustomUserManager
import uuid




class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, null=False, default="")
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(null=False)
    friends = models.ManyToManyField("self", blank=True)
    first_name = models.CharField(max_length=64, null=False)
    last_name = models.CharField(max_length=64, null=False)
    profile_image = models.TextField(null=True, blank=True)
    is_online = models.BooleanField(null=False, default=False)
    last_date_online = models.DateTimeField(null=True, blank=True)
    channel_name = models.CharField(max_length=256, null=True, blank=True)
    is_channel_busy = models.BooleanField(null=True, blank=True, default=False)
    is_email_verified = models.BooleanField(null=False, default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Group(models.Model):
    group_id = models.CharField(primary_key=True, max_length=124, editable=False, null=False, default=uuid.uuid4)
    created_at = models.DateField(auto_now_add=True, editable=False)
    group_name = models.CharField(max_length=120, null=False, blank=False)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, related_name="group")
    participants = models.ManyToManyField(CustomUser, related_name="all_groups", blank=True)
    group_photo = models.TextField(null=True, blank=True)


class Message(models.Model):
    message_id = models.CharField(primary_key=True, max_length=124, editable=False, null=False)
    created_at = models.DateTimeField(null=False, editable=False)
    text = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    video = models.TextField(null=True, blank=True)
    audio = models.TextField(null=True, blank=True)
    file = models.TextField(null=True, blank=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="messages")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="messages")
    receipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="inbox")
    is_receipient_online = models.BooleanField(null=False, default=False)
    likes = models.IntegerField(default=0, null=False)

class IsGroupAdmin(models.Model):
    is_group_admin_id = models.CharField(primary_key=True, max_length=124, editable=False, null=False, default=uuid.uuid4)
    created_at = models.DateTimeField(null=False, default=datetime.now)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="is_group_admin")
    IsGroupAdmin = models.BooleanField(default=False, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="is_group_admin")