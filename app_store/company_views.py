import json

from django.http import JsonResponse
from django.views import View
from app_store.models import *

class StaffView(View):
    def get(self, request):
        print(request.GET)
        limit = int(request.GET.get('limit'))
        page = int(request.GET.get('page'))
        s_name = request.GET.get('s_name')
        s_roleId = int(request.GET.get('s_roleId'))
        s_departId = int(request.GET.get('s_departId'))

        staff_list = Staff.objects.all()
        staff_total = staff_list.count()

        if len(s_name) != 0:
            staff_list = staff_list.filter(name__contains=s_name)
        if s_roleId != -1:
            try:
                role_obj = Role.objects.get(id=s_roleId)
            except Role.DoesNotExist:
                return JsonResponse({'code': 400, 'message': '角色不存在'})
            staff_list = staff_list.filter(role=role_obj)
        if s_departId != -1:
            try:
                depart_obj = Depart.objects.get(id=s_departId)
            except Depart.DoesNotExist:
                return JsonResponse({'code': 400, 'message': '部门不存在'})
            staff_list = staff_list.filter(depart=depart_obj)

        staff_list = staff_list[(page-1)*limit:page*limit]
        staff_list = list(staff_list.values())
        response = {
            'code': 200,
            'message': '获取成功',
            'limit': limit,
            'page': page,
            'total': staff_total,
            'record': staff_list
        }

        return JsonResponse(response)

    def post(self, request):
        staff_post = json.loads(request.body)
        print(staff_post)
        try:
            role_obj = Role.objects.get(id=staff_post['role'])
        except Role.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '角色不存在'})


        staff_obj = Staff(name= staff_post['name'],
                          age=staff_post['age'],
                          salary=staff_post['salary'],
                          card=staff_post['card'],
                          phone=staff_post['telphone'],
                          role=role_obj,
                          depart=role_obj.depart)
        staff_obj.save()

        return JsonResponse({'code': 200, 'message': '新建成功'})

    def delete(self, request):
        id = request.GET.get('id')
        if id == None:
            return JsonResponse({'code': 400, 'message': 'id不能为空'})
        try:
            staff = Staff.objects.get(id=id)
        except Staff.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '员工不存在'})
        else:
            staff.delete()
            return JsonResponse({'code': 200, 'message': '删除成功'})

    def put(self, request):
        staff_put = json.loads(request.body)
        try:
            staff_obj = Staff.objects.get(id=staff_put['id'])
        except Staff.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '员工不存在'})

        try:
            role_obj = Role.objects.get(id=staff_put['roleId'])
        except Role.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '角色不存在'})

        staff_obj.age = staff_put['age']
        staff_obj.salary = staff_put['salary']
        staff_obj.card = staff_put['card']
        staff_obj.phone = staff_put['telphone']
        staff_obj.role = role_obj
        staff_obj.depart = role_obj.depart

        staff_obj.save()
        return JsonResponse({'code': 200, 'message': '修改成功'})

class DepartView(View):
    def get(self, request):
        departs_list = Depart.objects.all()
        departs_amount = departs_list.count()
        record = []
        for depart in departs_list:
            record.append({
                'id': depart.id,
                'name': depart.name
            })

        response = {
            'code': 200,
            'message': '获取成功',
            'total': departs_amount,
            'record': record
        }
        return JsonResponse(response)

class RoleView(View):
    def get(self, request):
        roles_list = Role.objects.all()
        roles_amount = roles_list.count()
        record = []
        for role in roles_list:
            record.append({
                'id': role.id,
                'parent': role.parent,
                'name': role.name
            })

        response = {
            'code': 200,
            'message': '获取成功',
            'total': roles_amount,
            'record': record
        }
        return JsonResponse(response)
