from app_store.models import *
from django.http import JsonResponse
from django.views import View
import json


def food_buy(request):
    if request != 'POST':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})
    post = json.loads(request.body)
    food_list = post['foodlist']
    try:
        user = Vip.objects.get(id=post['customer_id'])
    except Vip.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '用户不存在'})
    try:
        seat = Seat.objects.get(id=post['seat_id'])
    except Seat.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '座位不存在'})
    # TODO: 完成订单生成


def get_food_list(request):
    if request.method != 'GET':
        response = {
                'code': 400,
                'message': '方法错误'
                }
        return JsonResponse(response)

    food_list = Food.objects.all()
    list_info = []
    for food in food_list:
        # 根据自己类型找typeid
        list_info.append({
            'food_id': food.id,
            'food_type': food.type.title,
            'food_name': food.name,
            'food_price': food.price,
            'food_dealamount': food.deal_amount,
            'food_avatar': '/static/img/food_avatar/' + food.avatar
        })

    response = {
        'code': 200,
        'message': '获取成功',
        'list': list_info
    }
    return JsonResponse(response)