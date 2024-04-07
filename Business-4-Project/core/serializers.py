from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token

from core.models import CustomUserRoles
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser

UserModel = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user.is_deleted:
            raise serializers.ValidationError(
                "Your account has been deactivated. Please contact admin if this was a mistake.")

        return data

    def get_token(cls, user: AuthUser) -> Token:
        token = super().get_token(user)
        user.user_verification_key = get_random_string(length=12)
        user.save()
        token['user_verification_key'] = user.user_verification_key  # Include the verification key

        return token


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'is_staff', 'roles', 'is_deleted', 'first_name', 'last_name']

    def get_roles(self, user):
        roles = user.customuserroles_set.all()
        return [{'title': role.title,
                 'can_modify_module': role.can_modify_module,
                 'can_modify_category': role.can_modify_category,
                 'can_modify_user': role.can_modify_user,
                 'can_modify_roles': role.can_modify_roles,
                 'can_modify_files': role.can_modify_files} for role in roles]


class CustomUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserRoles
        exclude = ['user']
