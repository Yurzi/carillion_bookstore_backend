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
    path('v1/vip/review/', views.vip_review),

    # book:w
    path('v1/company/staff/', company_views.StaffView.as_view()),
    path('v1/company/department/', company_views.DepartView.as_view()),
    path('v1/company/role/', company_views.RoleView.as_view()),
    path('v1/book/info/', book_views.BookInfoView.as_view()),
    path('v1/press/info/', book_views.PublishInfoView.as_view()),
    path('v1/book/category/', book_views.get_book_category),
    path('v1/book/list/', book_views.get_book_sale_list),
    path('v1/book/avatar/', book_views.BookAvatarView.as_view()),
    path('v1/press/show/', book_views.put_press_show),
    path('v1/book/review/', book_views.get_book_reviews),
    path('v1/book/show/', book_views.put_book_show),

    # share
    path('v1/share/clicks/', share_views.get_share_clicks),
    path('v1/share/seatchange/', share_views.get_share_seatchange),
    path('v1/share/typebooklist/', share_views.get_type_book_list),
    path('v1/share/book/list/', share_views.get_book_share_list),
    path('v1/share/book/', share_views.post_share_book),
    path('v1/share/seatlist/', share_views.get_seat_list),
    path('v1/share/books/', share_views.get_type_four_book),
    path('v1/share/search/', share_views.get_book_search),

    # food
    path('v1/food/info/', food_views.FoodInfoView.as_view()),
    path('v1/food/avatar/', food_views.FoodAvatarView.as_view()),
    path('v1/food/type/', food_views.FoodTypeView.as_view()),

]
