import app_store.models
from app_store.models import *
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
import sys

import json

# 图书小食消费订单
def post_sale_order(request):
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse({'code': 400, 'message': str(e)})
    print(data)

    # 获取用户
    try:
        user = Vip.objects.get(id=data['customer_id'])
        book_list = data['booklist']
        food_list = data['foodlist']
        food_payprice = data['food_payprice']
        book_payprice = data['book_payprice']
        memo = data['memo']
    except Vip.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'code': 400, 'message': str(e)})
    if len(book_list) == 0 and len(food_list) == 0:
        return JsonResponse({'code': 400, 'message': '没有消费项目'})

    book_total_price = Decimal(0)
    food_total_price = Decimal(0)
    date = timezone.now()
    if len(book_list) > 0:
        # 生成预先的BookOrderV
        book_order_obj = BookOrder.objects.create(vip_id=user,
                                                    date=date,
                                                  status=1,
                                                  cust_name= user.name,
                                                  pay_price=book_payprice,
                                                  memo=memo)
        book_order_obj.save()

        # 生成BookOrderItem
        for book_item in book_list:
            try:
                book = Book.objects.get(id=book_item['book_id'])
                book_amount = book_item['book_num']
                book_amount = Decimal.from_float(book_amount)
            except Book.DoesNotExist:
                return JsonResponse({'code': 400, 'message': '图书不存在: id=' + book_item['book_id']})
            except Exception as e:
                return JsonResponse({'code': 400, 'message': str(e)})

            book_order_item = BookOrderItem.objects.create(order_id= book_order_obj,
                                                            book_id= book,
                                                            amount= book_amount,
                                                            total_price= book.price* book_amount,
                                                            pay_price= book.price * book_amount * Decimal.from_float(1 - 0.01 * user.level)
                                                           )
            book_order_item.save()
            book_total_price += book_order_item.total_price

        # 修改BookOrder
        book_order_obj.total_price = book_total_price
        book_order_obj.save()
        # 校验pay_price是否合法
        if abs(Decimal.from_float(book_order_obj.pay_price) - book_order_obj.total_price * Decimal.from_float(1 - 0.01 * user.level)) > 0.1:
            print(book_order_obj.pay_price, book_order_obj.total_price * Decimal.from_float(1 - 0.01 * user.level))
            book_order_obj.delete()
            return JsonResponse({'code': 400, 'message': 'book订单金额不合法'})
        # 生成Deal
        try:
            book_deal_obj = Deal.objects.create(vip_id=user,
                                                type=DealType.objects.get(title='book'),
                                                order_id=book_order_obj.id,
                                                amount=book_order_obj.pay_price,
                                                date=date)
            book_deal_obj.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'message': str(e)})
    if len(food_list) > 0:
        # 生成预先的FoodOrder
        try:
            food_order_obj = FoodOrder.objects.create(vip_id=user,
                                                      date=date,
                                                      status=1,
                                                      pay_price=food_payprice,
                                                      memo=memo)
            seat = Seat.objects.filter(condition=1).filter(vip_id=user).first()
            if seat is not None:
                food_order_obj.seat_id = seat
        except Exception as e:
            return JsonResponse({'code': 405, 'message': str(e)})
        food_order_obj.save()

        # 生成FoodOrderItem
        for food_item in food_list:
            try:
                food = Food.objects.get(id=food_item['food_id'])
                food_amount = food_item['food_num']
            except Food.DoesNotExist:
                return JsonResponse({'code': 400, 'message': '食品不存在: id=' + food_item['food_id']})
            except Exception as e:
                return JsonResponse({'code': 400, 'message': str(e)})

            food_order_item = FoodOrderItem.objects.create(order_id= food_order_obj,
                                                           food_id= food,
                                                           amount= food_amount,
                                                           total_price= food.price * food_amount,
                                                           pay_price= food.price * food_amount * Decimal.from_float(1 - 0.01 * user.level)
                                                           )
            food_order_item.save()
            food_total_price += food_order_item.total_price

        # 修改FoodOrder
        food_order_obj.total_price = food_total_price
        food_order_obj.save()
        # 校验pay_price是否合法
        if abs(Decimal.from_float(food_order_obj.pay_price) - food_order_obj.total_price * Decimal.from_float(1 - 0.01 * user.level)) > 0.1:
            food_order_obj.delete()
            return JsonResponse({'code': 400, 'message': 'food订单金额不合法'})
        # 生成Deal
        try:
            food_deal_obj = Deal.objects.create(vip_id=user,
                                                type=DealType.objects.get(title='food'),
                                                order_id=food_order_obj.id,
                                                amount=food_order_obj.pay_price,
                                                date=date)
            food_deal_obj.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'message': str(e)})

    return JsonResponse({'code': 200,
                         'message': '订单创建成功',
                         'total_price': book_total_price + food_total_price,
                         'pay_price': book_total_price + food_total_price * Decimal.from_float(1 - 0.01 * user.level),
                         })


# 获取所有账单
def get_deal_list(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        limit = int(request.GET.get('limit'))
        page = int(request.GET.get('page'))
        s_typeId = int(request.GET.get('s_typeId'))
        s_orderId = int(request.GET.get('s_orderId'))
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

    deal_list = Deal.objects.all()
    deal_total = deal_list.count()
    # print(deal_list)
    if s_typeId != -1:
        deal_list = deal_list.filter(type_id=s_typeId)
    if s_orderId != -1:
        deal_list = deal_list.filter(order_id=s_orderId)

    response = {
        'code': 200,
        'message': '获取成功',
        'limit': limit,
        'page': page,
        'total': deal_total,
        'record': []
    }
    deal_list = deal_list[(page - 1) * limit:page * limit]
    for deal in deal_list:
        temp = {
            'id': deal.id,
            'typeId': deal.type.id,
            'type': deal.type.title,
            'orderId': deal.order_id,
            'amount': deal.amount,
            'date': deal.date
        }
        # print(temp)
        response['record'].append(temp)

    return  JsonResponse(response)


# 按id发放员工薪水
def post_staff_salary_grant(request):
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        data = json.loads(request.body)
        id = data['id']
        amount = data['amount']
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

    try:
        staff = Staff.objects.get(id=id)
    except Staff.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '员工不存在'})

    date = timezone.now()
    # 生成SalaryOrder
    try:
        salary_order_obj = SalaryOrder.objects.create(staff=staff,
                                                      amount=amount,
                                                      date=date,
                                                      status=1)
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

    salary_order_obj.save()

    # 生成Deal
    try:
        deal_obj = Deal.objects.create(type=DealType.objects.get(title='salary'),
                                       order_id=salary_order_obj.id,
                                       amount=salary_order_obj.amount,
                                       date=date)
    except DealType.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '账单类型不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

    deal_obj.save()
    return JsonResponse({'code': 200, 'message': '发放成功'})


# 用户购买订单
def get_user_deal(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        user = Vip.objects.get(id=request.GET.get('id'))
    except Vip.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})
    try:
        deal_type=DealType.objects.get(title='salary')
    except DealType.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '账单类型不存在'})

    deal_list = Deal.objects.filter(vip_id=user).exclude(type_id=deal_type)

    response = {
        'code': 200,
        'message': '获取成功',
        'record': []
    }

    for deal in deal_list:
        temp = {
            'id': deal.id,
            'typeId': deal.type.id,
            'type': deal.type.title,
            'orderId': deal.order_id,
            'amount': deal.amount,
            'date': deal.date
        }
        response['record'].append(temp)

    return JsonResponse(response)


# 获取对应订单id的VIP订单
def get_vip_order_by_id(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})


    try:
        order_id = int(request.GET.get('order_id'))
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e), 'line': sys._getframe().f_lineno})

    order_obj = VipOrder.objects.filter(id=order_id).first()
    if order_obj is None:
        return JsonResponse({'code': 400, 'message': '订单不存在'})
    response = {
        'code': 200,
        'message': '获取成功',
        'order': {
            'vip_id': order_obj.vip_id.id,
            'vip_name': order_obj.vip_id.name,
            'date': order_obj.date,
            'total_price': order_obj.total_price,
            'pay_price': order_obj.pay_price,
            'status': order_obj.status,
        }
    }

    return JsonResponse(response)


# 获取对应订单id的员工订单
def get_salary_order_by_id(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        order_id = int(request.GET.get('order_id'))
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e), 'line': sys._getframe().f_lineno})

    order_obj = SalaryOrder.objects.filter(id=order_id).first()
    if order_obj is None:
        return JsonResponse({'code': 400, 'message': '订单不存在'})

    response = {
        'code': 200,
        'message': '获取成功',
        'order': {
            'staff_id': order_obj.staff.id,
            'staff_name': order_obj.staff.name,
            'date': order_obj.date,
            'amount': order_obj.amount,
            'status': order_obj.status,
        }
    }

    return JsonResponse(response)


# 获取对应订单id的图书订单
def get_book_order_by_id(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        order_id = int(request.GET.get('order_id'))
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e), 'line': sys._getframe().f_lineno})
    order_obj = BookOrder.objects.filter(id=order_id).first()
    if order_obj is None:
        return JsonResponse({'code': 400, 'message': '订单不存在'})

    response = {
        'code': 200,
        'message': '获取成功',
        'order': {
            'vip_id': order_obj.vip_id.id,
            'vip_name': order_obj.vip_id.name,
            'vip_level': order_obj.vip_id.level,
            'date': order_obj.date,
            'total_price': order_obj.total_price,
            'pay_price': order_obj.pay_price,
            'status': order_obj.status,
            'memo': order_obj.memo,
            'order_items': []
        }
    }

    order_item_list = order_obj.order_item.all()
    for order_item in order_item_list:
        temp = {
            'book_id': order_item.book_id.id,
            'book_name': order_item.book_id.name,
            'price': order_item.book_id.price,
            'total_price': order_item.total_price,
            'pay_price': order_item.pay_price,
        }
        response['order']['order_items'].append(temp)

    return JsonResponse(response)


# 获取对应订单id的食物订单
def get_food_order_by_id(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        order_id = int(request.GET.get('order_id'))
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e), 'line': sys._getframe().f_lineno})

    order_obj = FoodOrder.objects.filter(id=order_id).first()
    if order_obj is None:
        return JsonResponse({'code': 400, 'message': '订单不存在'})

    response = {
        'code': 200,
        'message': '获取成功',
        'order': {
            'vip_id': order_obj.vip_id.id,
            'vip_name': order_obj.vip_id.name,
            'vip_level': order_obj.vip_id.level,
            'date': order_obj.date,
            'total_price': order_obj.total_price,
            'pay_price': order_obj.pay_price,
            'status': order_obj.status,
            'memo': order_obj.memo,
            'order_items': []
        }
    }

    order_item_list = order_obj.order_item.all()
    for order_item in order_item_list:
        temp = {
            'food_id': order_item.food_id.id,
            'food_name': order_item.food_id.name,
            'price': order_item.food_id.price,
            'total_price': order_item.total_price,
            'pay_price': order_item.pay_price,
        }
        response['order']['order_items'].append(temp)

    return JsonResponse(response)