import time
from app_store.models import *
from django.http import JsonResponse
from django.views import View


# 增加点击量
def get_share_clicks(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    book_id = request.GET.get('id')
    if book_id is None:
        return JsonResponse({'code': 400, 'message': 'id不能为空'})
    try:
        book_obj = Book.objects.get(id=int(book_id))
    except Book.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '图书不存在'})
    book_obj.look_amount += 1
    book_obj.save()

    response = {
        'code': 200,
        'message': '修改成功',
        'clickNum': book_obj.look_amount
    }
    return JsonResponse(response)


# 座位变更
def get_share_seatchange(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    seat_id = request.GET.get('id')
    cos_id = request.GET.get('cosid')
    try:
        seat_id = int(seat_id)
        cos_id = int(cos_id)
    except ValueError:
        return JsonResponse({'code': 400, 'message': '参数类型有误'})

    now_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        seat_obj = Seat.objects.get(id=seat_id)
    except Seat.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '座位不存在'})
    seat_obj.update(vip_id=cos_id)
    seat_obj.update(date=now_date)
    seat_obj.update(condition=1)

    response = {
        'code': 200,
        'message': '选座成功',
        'date': now_date
    }
    return JsonResponse(response)
