from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import json, datetime, time, re
from django.urls import resolve, reverse
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.db import transaction


class MenuHelper(object):
    def __init__(self, request):
        self.request = request  # 当前请求的request对象
        self.current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
        self.authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
        self.menu_leaf_list = request.session.get('menu_leaf_list')  # 获取在菜单中显示的权限
        self.menu_list = request.session.get('menu_list')  # 获取所有菜单

    def menu_data_list(self):
        menu_leaf_dict = {}  # 有菜单权限字典
        open_leaf_parent_id = None
        # 归并所有的叶子节点
        for item in self.menu_leaf_list:
            item = {
                'id': item['id'],
                'url': item['url'],
                'url_name': item['url_name'],
                'caption': item['name'],
                'parent_id': item['carte'],
                'child': [],
                'status': True,  # 是否显示
                'open': False,
            }  # 替换每个字典的键
            if item['parent_id'] in menu_leaf_dict:
                menu_leaf_dict[item['parent_id']].append(item)
            else:
                menu_leaf_dict[item['parent_id']] = [item, ]
            # if re.match(item['url'], current_url):
            if item['url_name'] == self.current_url_name:
                item['open'] = True
                open_leaf_parent_id = item['parent_id']
        # 获取所有菜单字典
        '''将列表menu_list转换为字典，'''
        menu_dict = {}  # 菜单字典
        for item in self.menu_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
            item['child'] = []  # 将carte_list里的每个字典添加一个child键，值设置为一个空列表
            menu_dict[item['id']] = item  # 将字典carte_dict键设为item字典的id值，值设为item字典
            item['status'] = False
            item['open'] = False
        # 将叶子节点添加到菜单中
        for k, v in menu_leaf_dict.items():
            menu_dict[k]['child'] = v  # 将权限挂到菜单上
            parent_id = k
            # 将后代中有叶子节点的菜单标记为【显示】
            while parent_id:
                menu_dict[parent_id]['status'] = True
                parent_id = menu_dict[parent_id]['parent_id']
        # 将已经选中的菜单标记为【展开】
        while open_leaf_parent_id:
            menu_dict[open_leaf_parent_id]['open'] = True
            open_leaf_parent_id = menu_dict[open_leaf_parent_id]['parent_id']

        menu_result = []
        for row in menu_dict.values():
            if not row['parent_id']:
                menu_result.append(row)
            else:
                menu_dict[row['parent_id']]['child'].append(row)
        return menu_result


def acc_login(request):
    ''':param request::return:'''
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print("acc_login-->request.POST.get('username'):", username)
        print("acc_login-->request.POST.get('password'):", password)
        print("acc_login-->request.POST.get('code'):", code)
        user = authenticate(username=username, password=password)
        print('user:', user)
        if user:
            job_list_d = list(user.job.all().values('name'))  # 角色列表
            job_list = []
            for job in job_list_d:
                job_list.append(job["name"])
            request.session['job_list'] = job_list
            authority_list_d = list(models.Authorities.objects.filter(
                jobs__employees=user).distinct().values('url_name'))  # 权限列表
            authority_list = []
            for authority in authority_list_d:
                authority_list.append(authority["url_name"])
            request.session['authority_list'] = authority_list
            '''# 获取菜单的叶子节点，即：菜单的最后一层应该显示的权限'''
            menu_leaf_list = list(models.Authorities.objects.filter(
                jobs__employees=user).distinct().order_by('ordery').exclude(
                carte__isnull=True).values(
                'id', 'name', 'url', 'url_name', 'carte', 'ordery'))  # 有菜单权限列表
            request.session['menu_leaf_list'] = menu_leaf_list
            menu_list = list(models.Cartes.objects.filter(
                authority_carte__jobs__employees=user).distinct().order_by('ordery').values(
                'ordery', 'id', 'caption', 'parent_id'))  # # 获取所有的菜单列表
            request.session['menu_list'] = menu_list

            login(request, user)

            return redirect(request.GET.get('next', 'dbms:index'))
        else:
            error_msg = "用户名或密码错误！"

    return render(request, 'login.html', {'error_msg': error_msg})


def authority(func):
    def inner(request, *args, **kwargs):
        current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
        authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
        # today_stamp = time.mktime(datetime.date.today())  # 元组转换为时间戳
        limit_date = '2020-12-31'
        limit_date_tup = time.strptime(limit_date, "%Y-%m-%d")  # 字符串转换为元组
        limit_date_stamp = time.mktime(limit_date_tup)  # 元组转换为时间戳

        today_str = str(datetime.date.today())  # 元组转换为字符串
        today_tup = time.strptime(today_str, "%Y-%m-%d")  # 字符串转换为元组
        today_stamp = time.mktime(today_tup)  # 元组转换为时间戳
        if not current_url_name in authority_list:
            response = {'status': True, 'message': None}
            response['status'] = False
            response['message'] = '无权限，请联系管理员！'
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
        elif today_stamp > limit_date_stamp:
            response = {'status': True, 'message': None}
            response['status'] = False
            response['message'] = ''
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
        print(request.user, '>', request.path, '>', resolve(request.path).url_name, '>', request.POST, )
        return func(request, *args, **kwargs)

    return inner


def acc_logout(request):
    logout(request)
    return redirect('login')


@login_required
# @authority
def home(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    print('request.path_info', request.path_info)  # 当前url
    print('request.path:', request.path)
    print('resolve(request.path):', resolve(request.path))  # 路径转换为url_name等
    print('resolve(request.path):', resolve(request.path).url_name)  # 路径转换为url_name、app_name
    print('reverse(request.path):', reverse('home'))  # 将路径名转换为路径
    print('request.get_host:', request.get_host())
    print('request.GET.items():', request.GET.items())  # 获取get传递的参数对
    print('acc_login-->request.COOKIES:', request.COOKIES)
    print('acc_login-->request.session:', request.session)
    print('acc_login-->request.GET:', request.GET)
    print("request.session.get('authority_list'):", request.session.get('authority_list'))
    print("request.session.get('menu_leaf_list'):", request.session.get('menu_leaf_list'))

    return render(request, 'test.html', locals())


def Caltime(date1, date2):
    # %Y-%m-%d为日期格式，其中的-可以用其他代替或者不写，但是要统一，同理后面的时分秒也一样；可以只计算日期，不计算时间。
    # date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    # date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1 = time.strptime(date1, "%Y-%m-%d")
    date2 = time.strptime(date2, "%Y-%m-%d")
    # 根据上面需要计算日期还是日期时间，来确定需要几个数组段。下标0表示年，小标1表示月，依次类推...
    # date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    # date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    date1 = datetime.datetime(date1[0], date1[1], date1[2])
    date2 = datetime.datetime(date2[0], date2[1], date2[2])
    # 返回两个变量相差的值，就是相差天数
    return date2 - date1
