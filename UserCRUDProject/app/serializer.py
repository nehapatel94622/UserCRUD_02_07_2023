from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'first_name', 'last_name']

class UserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return ' '.join([obj.first_name, obj.last_name])

    class Meta:
        model = UserModel
        fields = ['id', 'name']

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField('get_email')
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    class Meta:
        model = ProfileModel
        fields = "__all__"