import os.path

from app_store.models import *
from django.http import JsonResponse
from django.views import View
from PIL import Image
import json
import hashlib


class BookInfoView(View):
    # 按id获取图书
    def get(self, request):
        id = request.GET.get('id')
        if id is None:
            return JsonResponse({'code': 400, 'message': 'id不能为空'})

        try:
            book_obj = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '图书不存在'})
        book_info = {
            'code': 200,
            'message': '获取成功',
            'record': [
                {
                    'id': book_obj.id,
                    'categoryId': book_obj.type.id,
                    'categoryName': book_obj.type.title,
                    'name': book_obj.name,
                    'pressId': book_obj.press.id,
                    'pressName': book_obj.press.name,
                    'pubDate': book_obj.pub_data,
                    'version': book_obj.version,
                    'author': book_obj.author,
                    'price': book_obj.price,
                    'page': book_obj.page,
                    'desc': book_obj.desc,
                    'dealamount': book_obj.deal_amount,
                    'lookamount': book_obj.look_amount,
                    'pic': '/static/img/book_avatar/' + book_obj.pic,
                    'isShow': book_obj.is_show
                }
            ]
        }
        return JsonResponse(book_info)

    # 创建新图书
    def post(self, request):
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
                is_show=post['isShow']
            )
        except KeyError:
            return JsonResponse({'code': 404, 'message': '数据键值对不完全'})
        book_obj.save()

        # 创建库存表项目
        book_store_obj = BookStore(
            book_id = book_obj,
            amount = 1,
            date=timezone.now()
        )
        book_store_obj.save()

        return JsonResponse({'code': 200, 'message': '新建成功', 'id': book_obj.id})

    # 按id修改图书
    def put(self, request):
        put = json.loads(request.body)
        if put is None:
            return JsonResponse({'code': 400, 'message': 'put不能为空'})
        try:
            book_obj = Book.objects.get(id=put['id'])
        except Book.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '图书不存在'})
        try:
            type_obj = BookType.objects.get(id=put['categoryId'])
        except BookType.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '图书类型不存在'})
        try:
            press_obj = Press.objects.get(id=put['pressId'])
        except Press.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '出版社不存在'})

        try:
            book_obj.type = type_obj
            book_obj.name = put['name']
            book_obj.press = press_obj
            book_obj.pub_data = datetime.strptime(put['pubDate'], '%Y-%m-%d').date()
            book_obj.version = put['version']
            book_obj.author = put['author']
            book_obj.desc = put['desc']
            book_obj.page = put['page']
            book_obj.price = put['price']
            book_obj.is_show = put['isShow']
            book_obj.deal_amount = put['dealamount']
            book_obj.look_amount = put['lookamount']
        except KeyError:
            return JsonResponse({'code': 404, 'message': '数据键值对不完全'})
        book_obj.save()

        return JsonResponse({'code': 200, 'message': '修改成功'})

    # 按id删除图书
    def delete(self, request):
        id = request.GET.get('id')
        if id is None:
            return JsonResponse({'code': 399, 'message': 'id不能为空'})

        try:
            book_obj = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '图书不存在'})

        book_obj.delete()
        return JsonResponse({'code': 200, 'message': '删除成功'})


class PublishInfoView(View):
    def get(self, request):
        try:
            limit = int(request.GET.get('limit'))
            page = int(request.GET.get('page'))
            s_name = request.GET.get('s_name')
            pub_list = Press.objects.all()
            pub_total = pub_list.count()
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})

        try:
            if len(s_name) > 0:
                pub_list = pub_list.filter(name__contains=s_name)
        except TypeError:
            return JsonResponse({'code': 400, 'message': '查询参数错误:s_name'})

        pub_list = pub_list[(page - 1) * limit:page * limit]
        response = {
            'code': 200,
            'message': '获取成功',
            'limit': limit,
            'page': page,
            'total': pub_total,
            'record': []
        }
        for item in pub_list:
            temp = {
                'id': item.id,
                'name': item.name,
                'show': int(item.is_show),
                'bookNum': item.book.count()
            }
            response['record'].append(temp)

        return JsonResponse(response)

    def post(self, request):
        post = json.loads(request.body)
        print(post)
        if post is None:
            return JsonResponse({'code': 400, 'message': 'post不能为空'})
        try:
            pub_obj = Press(
                name=post['name']
            )
        except KeyError:
            return JsonResponse({'code': 404, 'message': '数据键值对不完全'})
        pub_obj.save()
        return JsonResponse({'code': 200, 'message': '新建成功'})

    def put(self, request):
        put = json.loads(request.body)
        print(put)
        if put is None:
            return JsonResponse({'code': 400, 'message': 'post不能为空'})
        try:
            pub_obj = Press.objects.get(id=put['id'])
        except Press.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '出版社不存在'})
        try:
            pub_obj.name = put['name']
        except KeyError:
            return JsonResponse({'code': 404, 'message': '数据键值对不完全'})
        pub_obj.save()
        return JsonResponse({'code': 200, 'message': '修改成功'})

    def delete(self, request):
        id = request.GET.get('id')
        if id is None:
            return JsonResponse({'code': 399, 'message': 'id不能为空'})
        try:
            pub_obj = Press.objects.get(id=id)
        except Press.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '出版社不存在'})
        pub_obj.delete()

        return JsonResponse({'code': 200, 'message': '删除成功'})


class BookAvatarView(View):
    def get(self, request):
        id = request.GET.get('id')
        if id is None:
            return JsonResponse({'code': 400, 'message': 'id不能为空'})

        try:
            book_obj = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '图书不存在'})
        book_info = {
            'code': 200,
            'message': '获取成功',
            'url': '/static/img/book_avatar/' + book_obj.pic
        }
        return JsonResponse(book_info)

    def post(self, request):
        id = request.POST.get('id')
        if id is None:
            return JsonResponse({'code': 400, 'message': 'id不能为空'})
        print(id)
        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '图书不存在'})
        img = request.FILES.get('img')
        file_type = ""
        response = {}
        if img:
            file_type = img.name.split('.')[-1]
            prefix = os.path.join(os.getcwd(), 'app_store/', 'static/', 'img/', 'book_avatar/')
            path = prefix + 'temp.' + file_type
            if img.multiple_chunks():
                file_yield = img.chunks()
                with open(path, 'wb') as f:
                    for chunk in file_yield:
                        f.write(chunk)
                    else:
                        print('大文件接受完毕')
            else:
                with open(path, 'wb') as f:
                    f.write(img.read())
                print('小文件接受完毕')

            response = {
                'code': 200,
                'message': '上传成功',
            }
            # 修改图片尺寸
            img_ori = Image.open(path)
            img_resize = img_ori.resize((2549, 3583), Image.ANTIALIAS)
            out_path = prefix + 'temp_resize.' + file_type
            img_resize.save(out_path)
            # 删除temp 文件
            os.remove(path)
            # 计算MD5
            fp = open(out_path, 'rb')
            md5 = hashlib.md5(fp.read()).hexdigest()
            fp.close()
            md5 = md5 + '.' + file_type
            try:
                os.rename(out_path, prefix + md5)
            except FileExistsError:
                os.remove(out_path)
            book.pic = md5
            book.save()
        else:
            response = {
                'code': 400,
                'message': '上传文件为空',
            }
        return JsonResponse(response)


def get_book_category(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})
    category_list = BookType.objects.all()
    total = category_list.count()
    category_list = list(category_list.values())
    response = {
        'code': 200,
        'message': '获取成功',
        'total': total,
        'record': category_list
    }
    return JsonResponse(response)


def get_book_sale_list(request):
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

    book_list = Book.objects.filter(is_share=False)
    book_total = book_list.count()
    if len(s_name) > 0:
        book_list = book_list.filter(name__contains=s_name)
    if len(s_pressName) > 0:
        try:
            press_obj = Press.objects.get(name=s_pressName)
        except Press.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '出版社不存在'})
        book_list = book_list.filter(press=press_obj)
    if s_status != -1:
        book_list = book_list.filter(is_show=bool(s_status))
    if s_categoryIds is not None:
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
            'author': item.author,
            'pressId': item.press.id,
            'pressName': item.press.name,
            'price': item.price,
            'dealamount': item.deal_amount,
            'pic': '/static/img/book_avatar/' + item.pic,
            'isShow': int(item.is_show),
        }
        response['record'].append(temp)
    return JsonResponse(response)


def get_book_reviews(request):
    if request.method != 'GET':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})
    book_list = Book.objects.all()
    book_total = book_list.count()
    book_offsale = book_list.filter(is_show=False).count()
    book_onsale = book_total - book_offsale

    response = {
        'code': 200,
        'message': '获取成功',
        'result': {
            'total': book_total,
            'onSale': book_onsale,
            'offSale': book_offsale
        }
    }

    return JsonResponse(response)


def put_press_show(request):
    if request.method != 'PUT':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})
    put = json.loads(request.body)
    try:
        press_obj = Press.objects.get(id=put['id'])
    except Press.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '出版社不存在'})
    except KeyError as e:
        return JsonResponse({'code': 400, 'message': str(e)})
    press_obj.is_show = put['show']
    press_obj.save()
    return JsonResponse({'code': 200, 'message': '修改成功'})

def put_book_show(request):
    if request.method != 'PUT':
        return JsonResponse({'code': 400, 'message': '请求方式错误'})
    put = json.loads(request.body)
    try:
        id = int(put['id'])
        show = bool(put['show'])
    except KeyError:
        return JsonResponse({'code': 400, 'message': '请求参数错误'})

    try:
        book_obj = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return JsonResponse({'code': 400, 'message': '图书不存在'})

    book_obj.is_show = bool(show)
    book_obj.save()
    return JsonResponse({'code': 200, 'message': '修改成功', 'show': book_obj.is_show})

