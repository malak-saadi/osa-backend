from rest_framework import serializers
from accounts.models import Profile, User


class PatientSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source="profile.address", required=False, allow_blank=True)
    birthdate = serializers.DateField(source="profile.birthdate", required=False, allow_null=True)
    bio = serializers.CharField(source="profile.bio", required=False, allow_blank=True)
    image = serializers.ImageField(source="profile.image", required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "telephone",
            "role",
            "created_at",
            "address",
            "birthdate",
            "bio",
            "image",
        ]
        read_only_fields = ["id", "role", "created_at"]

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("Username is required.")
        return username

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError("Email is required.")
        return email

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=None,
            telephone=validated_data.get("telephone", ""),
            role=User.Role.PATIENT,
        )

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.address = profile_data.get("address", profile.address)
        profile.birthdate = profile_data.get("birthdate", profile.birthdate)
        profile.bio = profile_data.get("bio", profile.bio)
        profile.image = profile_data.get("image", profile.image)
        profile.save()

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})

        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.telephone = validated_data.get("telephone", instance.telephone)
        instance.save()

        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.address = profile_data.get("address", profile.address)
        profile.birthdate = profile_data.get("birthdate", profile.birthdate)
        profile.bio = profile_data.get("bio", profile.bio)
        profile.image = profile_data.get("image", profile.image)
        profile.save()

        return instance