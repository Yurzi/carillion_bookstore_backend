from django.shortcuts import HttpResponse, render
from django.http import JsonResponse, response
from django.db import IntegrityError
import json
import hashlib
import logging

from app_store.models import *

logger = logging.getLogger(__name__)

# Create your views here.
def test_connect(request):
    return JsonResponse({'code':200, 'message': '连接正常'})

def vip_register(request):
    if request.method != 'POST':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)
    post_user = {}
    if request.META['CONTENT_TYPE'] == 'application/json':
        post_user = json.loads(request.body)
    else:
        post_user['name'] = request.POST.get('name')
        post_user['password'] = request.POST.get('password')
        post_user['email'] = request.POST.get('email')

    logger.info("接受到:" + post_user.__str__())
    logger.debug("创建数据对象Vip...")
    user = Vip(
            name= post_user['name'],
            mail= post_user['email'],
            password= hashlib.sha256(post_user['password'].__str__().encode('utf-8')).hexdigest()
            )
    logger.debug("创建成功，写入数据库")
    response = {
            'message': '注册成功',
            'code': 200,
            'id': -1
            }
    try:
        user.save();
    except IntegrityError:
        response['code'] = 400
        response['message'] = "用户名已存在"
    else:
        response['id'] = user.id
    return JsonResponse(response)

def vip_login(request):
    if request.method != 'GET':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)

    username = request.GET.get('name')
    password = request.GET.get('password')
    password = hashlib.sha256(password.__str__().encode('utf-8')).hexdigest()

    # 查找用户
    user = Vip.objects.filter(name= username).first()
    if user == None:
        response = {
                'code': 404,
                'message': '用户不存在'
                }
        return JsonResponse(response)
    
    if user.password != password:
        response = {
                'code': 403,
                'message': '密码错误'
                }
        return JsonResponse(response)

    response = {
            'code': 200,
            'message': '登录成功',
            'person': {
                'vip_id': user.id,
                'vip_name': user.name,
                'vip_avatar': "/static/img/vip_avavtar/" + user.avatar,
                'vip_birthday': user.birthday,
                'vip_level': user.level,
                'vip_exp': user.exp,
                'vip_money': user.money,
                'vip_expireDate': user.expire_date,
                'vip_createData': user.create_date
                }
            }
    return JsonResponse(response)

def vip_avatar(request):
    if request.method != 'GET':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)
    user_id = request.GET.get('id')

    user = Vip.objects.filter(id= user_id).first()
    if user == None:
        response = {
                'code': 404,
                'message': '用户不存在'
                }
        return JsonResponse(response)
    response = {
            'code': 200,
            'message': '获取成功',
            'url': "/static/img/vip_avatar/" + user.avatar
            }
    return JsonResponse(response)

def vip_info(request):
    if request.method != 'GET':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)

    limit = int(request.GET.get('limit'))
    page = int(request.GET.get('page'))
    s_name = request.GET.get('s_name')
    s_level = request.GET.get('s_level')
    user_list = Vip.objects.all()
    user_total = len(user_list)

    if s_name == None and s_level == None:
        user_list = user_list[limit * (page - 1) : limit * page]
    elif s_name == None and s_level != None:
        user_list = user_list.filter(level= s_level)[limit * (page - 1) : limit * page]
    elif s_name != None and s_level != None:
        user_list = user_list.filter(name= s_name)[limit * (page - 1) : limit * page]
    else:
        user_list = user_list.filter(name= s_name, level= s_level)
    response = {
            'code': 201,
            'total': user_total,
            'limit': limit,
            'page': page,
            'record': [],
            'message': '获取成功'
            }
    for item in user_list:
        temp = {}
        temp['id'] = item.id
        temp['name'] = item.name
        temp['mail'] = item.mail
        temp['password'] = item.password
        temp['birthday'] = item.birthday
        temp['level'] = item.level
        temp['exp'] = item.exp
        temp['money'] = item.money
        temp['expireDate'] = item.expire_date
        temp['createDate'] = item.create_date
        response['record'].append(temp)

    return JsonResponse(response)
