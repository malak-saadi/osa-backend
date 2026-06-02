"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path , include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/patient/',      include('patient.urls')),
    path('api/statistique/',  include('statistique.urls')),
    path('api/v1/', include('apnea_analysis.urls')),
    path('', TemplateView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('sleep-history/', TemplateView.as_view(template_name='sleep_history.html'), name='sleep-history'),
    path('patient-profile/', TemplateView.as_view(template_name='patient_profile.html'), name='patient-profile'),
    path('settings/', TemplateView.as_view(template_name='settings.html'), name='settings'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
