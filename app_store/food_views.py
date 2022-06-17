import hashlib
import os

from app_store.models import *
from django.http import JsonResponse
from django.views import View
from PIL import Image
import json


class FoodTypeView(View):
    def get(self, request):
        food_type_list = FoodType.objects.all()
        total = food_type_list.count()

        food_type_list = list(food_type_list.values())
        response = {
            'code': 200,
            'message': '获取成功',
            'total': total,
            'list': food_type_list
        }
        return  JsonResponse(response)

    def post(self, request):
        data = json.loads(request.body)
        food_type_obj = FoodType.objects.create(title=data['title'])
        try :
            food_type_obj.save()
        except Exception as e:
            response = {
                'code': 500,
                'message': '类型添加失败',
                'error': str(e)
            }
            return JsonResponse(response)
        response = {
            'code': 200,
            'message': '添加成功',
            'id': food_type_obj.id
        }
        return JsonResponse(response)

    def delete(self,request):
        id = request.GET.get('id')
        try:
            food_type_obj = FoodType.objects.get(id=id)
        except FoodType.DoesNotExist:
            response = {
                'code': 404,
                'message': '类型不存在'
            }
            return JsonResponse(response)
        food_type_obj.delete()
        response = {
            'code': 200,
            'message': '删除成功'
        }
        return JsonResponse(response)


class FoodInfoView(View):
    def get(self, request):
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
                'food_avatar': '/static/img/food_avatar/' + food.avatar,
                'food_memo': food.memo,
            })

        response = {
            'code': 200,
            'message': '获取成功',
            'list': list_info
        }
        return JsonResponse(response)

    def post(self, request):
        post = json.loads(request.body)

        try:
            food_type = FoodType.objects.get(title=post['type'])
        except FoodType.DoesNotExist:
            response = {
                'code': 404,
                'message': '类型不存在'
            }
            return JsonResponse(response)

        food = Food(
            name=post['name'],
            price=post['price'],
            memo=post['memo'],
            type=food_type
        )

        food.save()
        food_store_obj = FoodStore(
            food_id = food,
            amount=1,
            date = timezone.now()
        )
        food_store_obj.save()

        response = {
            'code': 200,
            'message': '添加成功',
            'id': food.id
        }
        return JsonResponse(response)


    def put(self, request):
        post = json.loads(request.body)
        try:
            food_obj = Food.objects.get(id=post['id'])
        except Food.DoesNotExist:
            return JsonResponse({'code': 404, 'message': '食品不存在'})
        try:
            food_type = FoodType.objects.get(title=post['type'])
        except FoodType.DoesNotExist:
            return JsonResponse({'code': 404, 'message': '类型不存在'})
        try:
            food_obj.name = post['name']
            food_obj.price = post['price']
            food_obj.memo = post['memo']
            food_obj.type = food_type
            food_obj.deal_amount = post['dealamount']
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})

        food_obj.save()

        return JsonResponse({"code": 200, 'messgae': '修改成功'})

    def delete(self, request):
        id = request.GET.get('id')
        try:
            food_obj = Food.objects.get(id=id)
        except Food.DoesNotExist:
            response = {
                'code': 404,
                'message': '食品不存在'
            }
            return JsonResponse(response)
        food_obj.delete()
        response = {
            'code': 200,
            'message': '删除成功'
        }
        return JsonResponse(response)


class FoodAvatarView(View):
    def get(self, request):
        id = request.GET.get('id')
        try:
            food_obj = Food.objects.get(id=id)
        except Food.DoesNotExist:
            return JsonResponse({'code': 404, 'message': '食品不存在'})

        response = {
            'code': 200,
            'message': '获取成功',
            'url': '/static/img/food_avatar/' + food_obj.avatar
        }
        return JsonResponse(response)

    def post(self, request):
        try:
            id = request.POST.get('id')
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})
        print(id)
        try:
            food_obj = Food.objects.get(id=id)
        except Food.DoesNotExist:
            return JsonResponse({'code': 404, 'message': '食品不存在'})

        img = request.FILES.get('img')
        if img:
            file_type = img.name.split('.')[-1]
            prefix = os.path.join(os.getcwd(), 'app_store/', 'static/', 'img/', 'food_avatar/')
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
            img_resize = img_ori.resize((512, 512), Image.ANTIALIAS)
            out_path = prefix + 'temp_resize.' + file_type
            img_resize.save(out_path)

            # 删除temp文件
            os.remove(path)

            # 计算md5
            fp = open(out_path, 'rb')
            md5 = hashlib.md5(fp.read()).hexdigest()
            fp.close()
            md5 = md5 + '.' + file_type
            try:
                os.rename(out_path, prefix + md5)
            except FileExistsError:
                os.remove(out_path)

            food_obj.avatar = md5
            food_obj.save()
        else:
            response = {
                'code': 400,
                'message': '上传文件为空'
            }
        return JsonResponse(response)