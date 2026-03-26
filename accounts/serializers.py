from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile
class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'confirm_password', 'telephone', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'telephone', 'role', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    









# add these two classes to your existing serializers.py

# add these to serializers.py

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code  = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email            = serializers.EmailField()
    code             = serializers.CharField(max_length=6)
    new_password     = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
    








# add to serializers.py

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profile
        fields = ['id', 'bio', 'address', 'birthdate', 'image']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    # user info
    username  = serializers.CharField(source='user.username', required=False)
    email     = serializers.EmailField(source='user.email', required=False)
    telephone = serializers.CharField(source='user.telephone', required=False)

    class Meta:
        model  = Profile
        fields = ['username', 'email', 'telephone', 'bio', 'address', 'birthdate', 'image']

    def validate_email(self, value):
        user = self.instance.user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already used.")
        return value

    def validate_username(self, value):
        user = self.instance.user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def update(self, instance, validated_data):
        # extract user fields
        user_data = validated_data.pop('user', {})
        user = instance.user

        # update user fields
        user.username  = user_data.get('username',  user.username)
        user.email     = user_data.get('email',     user.email)
        user.telephone = user_data.get('telephone', user.telephone)
        user.save()

        # update profile fields
        instance.bio       = validated_data.get('bio',       instance.bio)
        instance.address   = validated_data.get('address',   instance.address)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.image     = validated_data.get('image',     instance.image)
        instance.save()

        return instance


class FullUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'telephone', 'role', 'created_at', 'profile']









    