"""carillion_bookstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path

from app_store import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('v1/test/connect/', views.test_connect),
    path('v1/vip/register/', views.vip_register),
    path('v1/vip/login/', views.vip_login),
    path('v1/vip/avatar/', views.vip_avatar),
    path('v1/vip/info/', views.vip_info),

]
