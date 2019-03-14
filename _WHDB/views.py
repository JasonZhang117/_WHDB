from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import json, datetime, time, re
from django.urls import resolve, reverse
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
                'id', 'caption', 'parent_id', 'ordery'))  # # 获取所有的菜单列表
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
        if not current_url_name in authority_list:
            response = {'status': True, 'message': None}
            response['status'] = False
            response['message'] = '无权限，请联系管理员！'
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
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

    # cooperator_list = models.Cooperators.objects.all()
    # for cooperator_obj in cooperator_list:
    #     cooperator_branch_flow_balance = models.Branches.objects.filter(
    #         cooperator=cooperator_obj).aggregate(
    #         Sum('branch_flow'))['branch_flow__sum']  # 授信银行项下，流贷余额
    #     if cooperator_branch_flow_balance:
    #         cooperator_list = models.Cooperators.objects.filter(id=cooperator_obj.id)
    #         cooperator_list.update(cooperator_flow=round(cooperator_branch_flow_balance, 2))
    #
    #     cooperator_branch_accept_balance = models.Branches.objects.filter(
    #         cooperator=cooperator_obj).aggregate(
    #         Sum('branch_accept'))['branch_accept__sum']  # 授信银行项下，流贷余额
    #     if cooperator_branch_accept_balance:
    #         cooperator_list = models.Cooperators.objects.filter(id=cooperator_obj.id)
    #         cooperator_list.update(cooperator_accept=round(cooperator_branch_accept_balance, 2))
    #
    #     cooperator_branch_back_balance = models.Branches.objects.filter(
    #         cooperator=cooperator_obj).aggregate(
    #         Sum('branch_back'))['branch_back__sum']  # 授信银行项下，流贷余额
    #     if cooperator_branch_back_balance:
    #         cooperator_list = models.Cooperators.objects.filter(id=cooperator_obj.id)
    #         cooperator_list.update(cooperator_back=round(cooperator_branch_back_balance, 2))

    # branch_list = models.Branches.objects.all()
    # for branch_obj in branch_list:
    #     '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
    #     branch_provide_1 = models.Provides.objects.filter(
    #         notify__agree__branch=branch_obj, provide_typ=1).aggregate(
    #         Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    #     if branch_provide_1:
    #         branch_list = models.Branches.objects.filter(id=branch_obj.id)
    #         branch_list.update(branch_flow=branch_provide_1)
    #
    #     branch_provide_11 = models.Provides.objects.filter(
    #         notify__agree__branch=branch_obj, provide_typ=11).aggregate(
    #         Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    #     if branch_provide_11:
    #         branch_list = models.Branches.objects.filter(id=branch_obj.id)
    #         branch_list.update(branch_accept=branch_provide_11)
    #
    #     branch_provide_21 = models.Provides.objects.filter(
    #         notify__agree__branch=branch_obj, provide_typ=21).aggregate(
    #         Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    #     if branch_provide_21:
    #         branch_list = models.Branches.objects.filter(id=branch_obj.id)
    #         branch_list.update(branch_back=branch_provide_21)

    # agree_list = models.Agrees.objects.all()  # 合同
    # for agree_obj in agree_list:
    #     agree_provide_balance = models.Provides.objects.filter(
    #         notify__agree=agree_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保余额合计
    #     if agree_provide_balance:
    #         print('agree_provide_balance:', agree_provide_balance)
    #         agree_list_l = models.Agrees.objects.filter(id=agree_obj.id)
    #         agree_list_l.update(agree_balance=round(agree_provide_balance, 2))  # 合同，更新放款总额
    #     else:
    #         agree_list_l = models.Agrees.objects.filter(id=agree_obj.id)
    #         agree_list_l.update(agree_balance=0)  # 合同，更新放款总额

    return render(request, 'index.html', locals())
