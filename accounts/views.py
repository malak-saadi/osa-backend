from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ChangePasswordSerializer ,ForgotPasswordSerializer,VerifyResetCodeSerializer,ResetPasswordSerializer
from .models import User , Profile

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .serializers import  ResetPasswordSerializer ,ProfileUpdateSerializer,FullUserSerializer
import random
from django.utils import timezone
from datetime import timedelta

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                'user':   UserSerializer(user).data,
                'tokens': tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            return Response({
                'user':   UserSerializer(user).data,
                'tokens': tokens,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"message": "Password changed successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deleted."}, status=status.HTTP_204_NO_CONTENT)





# add these imports at the top of views.py
import random
from django.utils import timezone


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]  # ✅ no login needed

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user  = User.objects.get(email=email)

            # generate 6-digit code
            code = str(random.randint(100000, 999999))

            # save code + expiry (15 minutes)
            user.reset_code        = code
            user.reset_code_expiry = timezone.now() + timedelta(minutes=15)
            user.save()

            # send email
            send_mail(
                subject="Password Reset Code",
                message=(
                    f"Hello {user.username},\n\n"
                    f"Your password reset code is:\n\n"
                    f"   {code}\n\n"
                    f"This code expires in 15 minutes.\n\n"
                    f"If you did not request this, ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({"message": f"Reset code sent to {email}."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code  = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "No account found with this email."}, status=status.HTTP_400_BAD_REQUEST)

            # check code matches
            if user.reset_code != code:
                return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

            # check code not expired
            if timezone.now() > user.reset_code_expiry:
                return Response({"error": "Code has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Code verified. You can now reset your password."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code  = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "No account found with this email."}, status=status.HTTP_400_BAD_REQUEST)

            # verify code again
            if user.reset_code != code:
                return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

            # check expiry again
            if timezone.now() > user.reset_code_expiry:
                return Response({"error": "Code has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            # set new password
            user.set_password(serializer.validated_data['new_password'])

            # clear the code after use
            user.reset_code        = None
            user.reset_code_expiry = None
            user.save()

            return Response({"message": "Password reset successfully. You can now login."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    







class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        # ✅ create profile if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        profile = self.get_profile(request.user)
        serializer = FullUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        profile = self.get_profile(request.user)
        serializer = ProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully.",
                "user": FullUserSerializer(request.user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  