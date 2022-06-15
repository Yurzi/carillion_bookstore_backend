from app_store.models import *
from django.http import JsonResponse
from django.views import View
import json


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
                    'categoryName': book_obj.type.name,
                    'name': book_obj.name,
                    'pressId': book_obj.press.id,
                    'pressName': book_obj.press.name,
                    'pubDate': book_obj.pub_date.timestamp(),
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




        return JsonResponse({'code': 200, 'message': 'post'})

    # 按id修改图书
    def put(self, request):
        return JsonResponse({'code': 200, 'message': 'put'})

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
    def get(self,request):
        limit = request.GET.get('limit')
        page = request.GET.get('page')
        s_name = request.GET.get('s_name')
        pub_list = Press.objects.all()
        pub_total = pub_list.count()

        if len(s_name) > 0:
            pub_list = pub_list.filter(name__contains=s_name)

        pub_list = pub_list[(page - 1) * limit:page * limit]
        pub_list = list(pub_list.values())
        response = {
            'code': 200,
            'message': '获取成功',
            'limit': limit,
            'page': page,
            'total': pub_total,
            'record': pub_list
        }

        return JsonResponse(response)

    def post(self, request):
        return JsonResponse({'code': 200, 'message': 'post'})

    def delete(self, request):
        return JsonResponse({'code': 200, 'message': 'delete'})

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
