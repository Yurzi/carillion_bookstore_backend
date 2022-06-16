import time
import json
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

    now_date = timezone.now()
    try:
        seat_obj = Seat.objects.get(id=seat_id)
    except Seat.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '座位不存在'})

    try:
        user_obj = Vip.objects.get(id=cos_id)
    except Vip.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '会员不存在'})

    if seat_obj.condition:
        if seat_obj.vip_id == user_obj:
            seat_obj.condition = 0
            seat_obj.vip_id = None
            seat_obj.save()
            return JsonResponse({'code': 400, 'message': '取消订座'})
        return JsonResponse({'code': 401, 'message': '座位已被占用'})
    seat_obj.vip_id = user_obj
    seat_obj.date = now_date
    seat_obj.condition = 1
    seat_obj.save()

    response = {
        'code': 200,
        'message': '选座成功',
        'date': now_date
    }
    return JsonResponse(response)


# 按照种类获取会员书架上的书
def get_type_book_list(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    limit = request.GET.get('limit')
    page = request.GET.get('page')
    type = request.GET.get('type')

    try:
        limit = int(limit)
        page = int(page)
        type = str(type)
    except ValueError:
        return JsonResponse({'code': 400, 'message': '参数类型有误'})

    try:
        type_obj = BookType.objects.get(title=type)
    except BookType.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '图书类型不存在'})

    book_list = ShareBook.objects.filter(book_id__type=type_obj)

    response = {
        'code': 200,
        'message': '获取成功',
        'record': []
    }
    for book_obj in book_list:
        temp = {
            'id': book_obj.book_id.id,
            'name': book_obj.book_id.name,
            'author': book_obj.book_id.author,
            'img': book_obj.book_id.pic,
            'date': book_obj.date,
            'lookAmount': book_obj.book_id.look_amount,
            'type': book_obj.book_id.type.title,
            'pages': book_obj.book_id.page,
            'outline': book_obj.book_id.desc,
            'version': book_obj.book_id.version,
            'vipName': book_obj.vip_id.name,
        }
        response['record'].append(temp)
    return JsonResponse(response)


# 获取用户分享图书列表
def get_book_share_list(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    try:
        limit = int(request.GET.get('limit'))
        page = int(request.GET.get('page'))
        s_name = request.GET.get('s_name')
        s_categoryIds = request.GET.get('s_categoryIds')
        s_pressName = request.GET.get('s_pressName')
        s_status = int(request.GET.get('s_status'))
    except:
        return JsonResponse({'code': 400, 'message': '请求参数错误'})

    book_list = Book.objects.filter(is_share=True)
    book_total = book_list.count()
    if len(s_name) > 0:
        # print(s_name)
        book_list = book_list.filter(name__contains=s_name)
    if len(s_pressName) > 0:
        # print(s_pressName)
        try:
            press_obj = Press.objects.get(name=s_pressName)
        except Press.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '出版社不存在'})
        book_list = book_list.filter(press=press_obj)
    if s_status != -1:
        # print(-1)
        book_list = book_list.filter(is_show=bool(s_status))
    if len(s_categoryIds) > 0:
        s_categoryIds = s_categoryIds.split(',')
        category_list = BookType.objects.filter(id__in=s_categoryIds)
        book_list = book_list.filter(type__in=category_list)

    book_list = book_list[(page - 1) * limit:page * limit]
    response = {
        'code': 200,
        'message': '获取成功',
        'limit': limit,
        'page': page,
        'total': book_total,
        'record': []
    }
    for item in book_list:
        temp = {
            'id': item.id,
            'categoryId': item.type.id,
            'categoryName': item.type.title,
            'name': item.name,
            'pressId': item.press.id,
            'pressName': item.press.name,
            'price': item.price,
            'dealamount': item.deal_amount,
            'pic': '/static/img/book_avatar/' + item.pic,
            'isShow': int(item.is_show),
        }
        response['record'].append(temp)
    return JsonResponse(response)


# 添加分享书籍
def post_share_book(request):
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})
    post = json.loads(request.body)
    print(post)
    if post is None:
        return JsonResponse({'code': 400, 'message': 'post不能为空'})
    try:
        type_obj = BookType.objects.get(id=post['categoryId'])
    except BookType.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '图书类型不存在'})
    try:
        press_obj = Press.objects.get(id=post['pressId'])
    except Press.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '出版社不存在'})

    try:
        user_obj = Vip.objects.get(id=post['vipId'])
    except Vip.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '会员不存在'})

    try:
        book_obj = Book(
            type=type_obj,
            name=post['name'],
            press=press_obj,
            pub_data=datetime.strptime(post['pubDate'], '%Y-%m-%d').date(),
            version=post['version'],
            author=post['author'],
            desc=post['desc'],
            page=post['page'],
            price=post['price'],
            is_show=post['isShow'],
            is_share=True
        )
    except KeyError:
        return JsonResponse({'code': 404, 'message': '数据键值对不完全'})
    book_obj.save()

    book_store_obj = BookStore(
        book_id=book_obj,
        amount=1,
        date=timezone.now()
    )
    book_store_obj.save()

    share_book_obj = ShareBook(vip_id= user_obj, book_id=book_obj, date=timezone.now())
    share_book_obj.save()

    return JsonResponse({'code': 200, 'message': '新建成功', 'book_id': book_obj.id, 'share_book_id': share_book_obj})


# 获取座位列表
def get_seat_list(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    seat_list = Seat.objects.all()
    response = {
        'code': 200,
        'message': '获取成功',
        'recordList': []
    }

    for item in seat_list:
        temp = {
            'id': item.id,
            'condition': item.condition,
            'date': item.date,
            'costId': -1
        }
        if bool(item.condition):
            try:
                temp['costId'] = item.vip_id.id
            except Exception as e:
                item.condition = 0
                item.save()
                temp['condition'] = 0
                response['error'] = str(e)

        response['recordList'].append(temp)

    return JsonResponse(response)


# 获取每种类型的前六种书
def get_type_four_book(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    # 取到所有类型
    type_list = BookType.objects.all()
    response = {
        'code': 200,
        'message': '获取成功',
        'booklist': []
    }
    for type_item in type_list:
        # 取到类型的前四本书
        book_list = ShareBook.objects.filter(book_id__type=type_item).order_by('-id')[:4]
        for book_item in book_list:
            temp = {
                'book_id': book_item.book_id.id,
                'book_type': book_item.book_id.type.title,
                'book_name': book_item.book_id.name,
                'book_press': book_item.book_id.press.name,
                'book_pubDate': book_item.book_id.pub_data,
                'book_version': book_item.book_id.version,
                'book_author': book_item.book_id.author,
                'book_price': book_item.book_id.price,
                'book_page': book_item.book_id.page,
                'book_desc': book_item.book_id.desc,
                'book_lookamount': book_item.book_id.look_amount,
                'book_pic': '/static/img/book_avatar/' + book_item.book_id.pic,
                'shareboook_date': book_item.date,
                'shareboook_vipname': book_item.vip_id.name,
                'type_id': book_item.book_id.type.id,
            }
            response['booklist'].append(temp)

    return JsonResponse(response)


# 获取搜索书籍
def get_book_search(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})

    pattern = request.GET.get('message')

    book_list_1 = ShareBook.objects.filter(book_id__name__contains=pattern, book_id__is_share=True)
    book_list_2 = ShareBook.objects.filter(book_id__press__name__contains=pattern, book_id__is_share=True)
    book_list_3 = ShareBook.objects.filter(book_id__type__title__contains=pattern, book_id__is_share=True)
    book_list_4 = ShareBook.objects.filter(book_id__author__contains=pattern, book_id__is_share=True)
    book_list_5 = ShareBook.objects.filter(book_id__desc__contains=pattern, book_id__is_share=True)
    book_list_6 = ShareBook.objects.filter(book_id__version__contains=pattern, book_id__is_share=True)

    book_list = book_list_1 | book_list_2 | book_list_3 | book_list_4 | book_list_5 | book_list_6

    book_list.distinct()
    response = {
        'code': 200,
        'message': '获取成功',
        'booklist': []
    }
    for book_item in book_list:
        temp = {
            'id': book_item.book_id.id,
            'categoryName': book_item.book_id.type.title,
            'name': book_item.book_id.name,
            'pressName': book_item.book_id.press.name,
            'pubDate': book_item.book_id.pub_data,
            'version': book_item.book_id.version,
            'author': book_item.book_id.author,
            'page': book_item.book_id.page,
            'price': book_item.book_id.price,
            'desc': book_item.book_id.desc,
            'lookamount': book_item.book_id.look_amount,
            'dealamount': book_item.book_id.deal_amount,
            'pic': '/static/img/book_avatar/' + book_item.book_id.pic,
            'shareboook_date': book_item.date,
            'shareboookPerson': book_item.vip_id.name,
        }
        response['booklist'].append(temp)
    return JsonResponse(response)

