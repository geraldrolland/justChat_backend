from rest_framework.serializers import ModelSerializer, CharField, Serializer
from .models import *


class CustomUserSerializer(ModelSerializer):
    password = CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        print("error in user")
        password = validated_data.pop("password")
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        print("user error")
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
                continue
            if value:
                setattr(instance, key, value)
        instance.save()
        return instance

class GroupSerialzer(ModelSerializer):


    class Meta:
        model = Group
        fields = "__all__"

class IsGroupAdminSerialzer(ModelSerializer):
    model = IsGroupAdmin

    class Meta:
        fields = "__all__"


class MessageSerialzer(ModelSerializer):


    class Meta:
        model = Message
        fields = "__all__"

class AuthSerializer(Serializer):
    code = CharField(required=False)
    error = CharField(required=False)