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
from app_store import book_views
from app_store import company_views
from app_store import food_views
from app_store import share_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('v1/test/connect/', views.test_connect),
    # vip
    path('v1/vip/register/', views.vip_register),
    path('v1/vip/login/', views.vip_login),
    path('v1/vip/avatar/', views.vip_avatar),
    path('v1/vip/info/', views.vip_info),
    path('v1/vip/recharge/', views.vip_recharge),
    path('v1/vip/update/', views.vip_info_update),
    path('v1/vip/updateAvatar/', views.vip_avatar_update),
    path('v1/vip/chargelist/', views.vip_charge_list),

    # book
    path('v1/company/staff/', company_views.StaffView.as_view()),
    path('v1/company/department/', company_views.DepartView.as_view()),
    path('v1/company/role/', company_views.RoleView.as_view()),
    path('v1/book/info/', book_views.BookInfoView.as_view()),
    path('v1/press/info/', book_views.PublishInfoView.as_view()),
    path('v1/book/category/', book_views.get_book_category),
    path('v1/book/list/', book_views.get_book_list),
    path('v1/book/avatar/', book_views.BookAvatarView.as_view()),
    # food
    path('v1/food/list/', food_views.get_food_list),
    path('v1/food/buy/', food_views.food_buy),
    path('v1/share/clicks/', share_views.get_share_clicks),
    path('v1/share/seatchange/', share_views.get_share_seatchange),
]
