from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/',        views.RegisterView.as_view()),
    path('login/',           views.LoginView.as_view()),
    path('logout/',          views.LogoutView.as_view()),
    path('me/',              views.MeView.as_view()),
    path('change-password/', views.ChangePasswordView.as_view()),
    path('delete/',          views.DeleteAccountView.as_view()),
    path('token/refresh/',   TokenRefreshView.as_view()),
     path('change-password/',  views.ChangePasswordView.as_view()),
   path('forgot-password/',   views.ForgotPasswordView.as_view()),
   path('verify-reset-code/', views.VerifyResetCodeView.as_view()),
   path('reset-password/',    views.ResetPasswordView.as_view()),
   path('profile/', views.ProfileView.as_view()),
]
