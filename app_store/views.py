from posixpath import splitext
from django.shortcuts import HttpResponse, render
from django.http import JsonResponse, QueryDict
from django.db import IntegrityError
from django.utils import timezone
import json
import hashlib
import logging
from datetime import datetime, timedelta
import os

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
                'vip_mail': user.mail,
                'vip_avatar': "/static/img/vip_avatar/" + user.avatar,
                'vip_birthday': user.birthday,
                'vip_level': user.level,
                'vip_exp': user.exp,
                'vip_money': user.money,
                'vip_expireDate': user.expire_date.timestamp(),
                'vip_createData': user.create_date.timestamp()
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
    s_level = int(request.GET.get('s_level'))
    user_list = Vip.objects.all()
    user_total = len(user_list)
    print(s_level)
    if s_level == -1:
        if len(s_name) != 0:
            user_list = user_list.filter(name= s_name)
    else:
        if len(s_name) == 0:
            user_list = user_list.filter(level= s_level)
        else:
            user_list = user_list.filter(level= s_level).filter(name= s_name)

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
        temp['expireDate'] = item.expire_date.timestamp()
        temp['createDate'] = item.create_date.timestamp()
        response['record'].append(temp)

    return JsonResponse(response)

def vip_recharge(request):
    if request.method != 'POST':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)
    post = {}
    if request.META['CONTENT_TYPE'] == 'application/json':
        post = json.loads(request.body)
    else:
        post['id'] = request.POST.get('id')
        post['money'] = request.POST.get('money')

    exp_gear = [0, 45, 260, 730, 990, 1890, 4320]
    date_gear = {
            '148': 365,
            '45': 90,
            '15': 30,
            '25': 30,
            '168': 356
            }
    user = Vip.objects.filter(id= post['id']).first()
    user.exp += post['money']
    response = {}
    try:
        if user.expire_date < user.create_date:
            user.expire_date = timezone.now() + timedelta(days= date_gear[str(post['money'])])
        else:
            user.expire_date += timedelta(days= date_gear[str(post['money'])])

        level = 0
        for item in exp_gear:
            level += 1
            if user.exp >= item:
                user.level = level
            else:
                break;

    except KeyError:
        response = {
                'code': 404,
                'message': '不存在这样的档位'
                }
    else:
        user.save()
        vip_order = VipOrder.objects.create(vip_id= user,date= timezone.now(), total_price= post['money'], pay_price= post['money'], status= 1)
        vip_order.save()
        deal_type = DealType.objects.filter(title= 'vip').first()
        deal = Deal.objects.create(type= deal_type, order_id= vip_order.id, amount= post['money'], date= timezone.now())
        deal.save() 
        response = {
                'code': 200,
                'message': "充值成功",
                'level': user.level,
                'lastingtime': (user.expire_date - timezone.now()).days
                }

    return JsonResponse(response)

def vip_info_update(request):
    if request.method != 'POST':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)
    post = {}
    if request.META['CONTENT_TYPE'] == 'application/json':
        post = json.loads(request.body)
    else:
        post['id'] = request.POST.get('id')
        post['mail'] = request.POST.get('mail')
        post['birthday'] = request.POST.get('birthday')
        post['password'] = request.POST.get('password')

    user = Vip.objects.filter(id= post['id']).first()

    if user == None:
        response = {
                'code': 404,
                'message': '用户不存在'
                }
        return JsonResponse(response)
    birthday = post['birthday']
    birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
    password = hashlib.sha256(post['password'].__str__().encode('utf-8')).hexdigest()

    if post['birthday'] != None: user.main= post['mail']
    if post['birthday'] != None: user.birthday = birthday
    if post['password'] != None: user.password = password

    user.save()

    response = {
            'code': 200,
            'message': '更新成功',
            }
    return JsonResponse(response)

def vip_avatar_update(request):
    if request.method != 'POST':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)
    print(request.META['CONTENT_TYPE'])
    id = request.POST.get('id')
    user = Vip.objects.filter(id= id).first()
    if user == None:
        response = {
                'code': 404,
                'message': '用户不存在'
                }

    img = request.FILES.get('img')
    file_type = ""
    response = {}
    if img:
        file_type = img.name.split('.')[-1]
        prefix = os.path.join(os.getcwd(), 'app_store/', 'static/', 'img/', 'vip_avatar/') 
        path = prefix + 'temp.' + file_type
        if img.multiple_chunks():
            file_yield = img.chunks()
            with open(path, 'wb') as f:
                for buf in file_yield:
                    f.write(buf)
                else:
                    logger.debug("大文件接受完毕")
        else:
            with open(path, "wb") as f:
                f.write(img.read())
            logger.debug('小文件接受完毕')
        response = {
                'code': 200,
                'message': '文件上传成功'
                }
        fp = open(path, 'rb')
        md5 = hashlib.md5(fp.read()).hexdigest()
        fp.close()
        md5 = md5 + '.' + file_type
        try:
            os.rename(path, prefix + md5)
        except FileExistsError:
            os.remove(path)
        user.avatar = md5
        user.save()
    else:
        response = {
                'code': 400,
                'message': '文件上传为空'
                }
   
    return JsonResponse(response)
