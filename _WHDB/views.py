from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import json, datetime, time, re
from django.urls import resolve, reverse
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.db import transaction
from dateutil.relativedelta import relativedelta

TTN = '成都武侯中小企业融资担保有限责任公司'
UND = '成都武侯中小企业融资担保有限责任公司'
UNX = '成都武侯武兴小额贷款有限责任公司'

FICATION_LIST = [(11, '正常'), (21, '关注'), (31, '次级'), (41, '可疑'), (51, '损失')]


class MenuHelper(object):
    def __init__(self, request):
        self.request = request  # 当前请求的request对象
        self.current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
        self.authority_list = request.session.get(
            'authority_list')  # 获取当前用户的所有权限
        self.menu_leaf_list = request.session.get(
            'menu_leaf_list')  # 获取在菜单中显示的权限
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
                menu_leaf_dict[item['parent_id']] = [
                    item,
                ]
            # if re.match(item['url'], current_url):
            if item['url_name'] == self.current_url_name:
                item['open'] = True
                open_leaf_parent_id = item['parent_id']
        # 获取所有菜单字典
        '''将列表menu_list转换为字典，'''
        menu_dict = {}  # 菜单字典
        for item in self.menu_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
            item['child'] = []  # 将carte_list里的每个字典添加一个child键，值设置为一个空列表
            menu_dict[
                item['id']] = item  # 将字典carte_dict键设为item字典的id值，值设为item字典
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


# ---------------------------登陆函数----------------------------#
def acc_login(request):
    ''':param request::return:'''
    # print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    request.session.clear_expired()  # 将所有Session失效日期小于当前日期的数据删除
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # print("acc_login-->request.POST.get('username'):", username)
        # print("acc_login-->request.POST.get('password'):", password)
        # print("acc_login-->request.POST.get('code'):", code)
        user = authenticate(username=username, password=password)
        # print('user:', user)
        if user:
            job_list_d = list(user.job.all().values('name'))  # 角色列表
            job_list = []
            for job in job_list_d:
                job_list.append(job["name"])
            request.session['job_list'] = job_list
            authority_list_d = list(
                models.Authorities.objects.filter(jobs__employees=user).
                distinct().values('url_name'))  # 权限列表
            authority_list = []
            for authority in authority_list_d:
                authority_list.append(authority["url_name"])
            request.session['authority_list'] = authority_list
            '''# 获取菜单的叶子节点，即：菜单的最后一层应该显示的权限'''
            menu_leaf_list = list(
                models.Authorities.objects.filter(
                    jobs__employees=user).distinct().order_by(
                        'ordery').exclude(carte__isnull=True).values(
                            'id', 'name', 'url', 'url_name', 'carte',
                            'ordery'))  # 有菜单权限列表
            request.session['menu_leaf_list'] = menu_leaf_list
            menu_list = list(
                models.Cartes.objects.filter(
                    authority_carte__jobs__employees=user).distinct().order_by(
                        'ordery').values('ordery', 'id', 'caption',
                                         'parent_id'))  # # 获取所有的菜单列表
            request.session['menu_list'] = menu_list

            login(request, user)

            return redirect(request.GET.get('next', 'dbms:index'))
        else:
            error_msg = "用户名或密码错误！"

    return render(request, 'login.html', {'error_msg': error_msg})


# ---------------------------登出函数----------------------------#
def acc_logout(request):
    logout(request)
    return redirect('login')


# ---------------------------项目筛选函数----------------------------#
def article_list_screen(article_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        article_list = article_list.filter(
            director__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return article_list
    elif '项目经理' in job_list:
        article_list = article_list.filter(
            Q(director=request_user)
            | Q(assistant=request_user))  # 用户为项目经理或助理项目
        return article_list
    else:
        return article_list


# ---------------------------合同筛选函数----------------------------#
def agree_list_screen(agree_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        agree_list = agree_list.filter(
            lending__summary__director__department=user_department
        )  # 项目经理部门与用户所属部门相同项目
        return agree_list
    elif '项目经理' in job_list:
        agree_list = agree_list.filter(
            Q(lending__summary__director=request_user)
            | Q(lending__summary__assistant=request_user))  # 用户为项目经理或助理项目
        return agree_list
    else:
        return agree_list


# ---------------------------放款通知筛选函数----------------------------#
def notify_list_screen(notify_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        notify_list = notify_list.filter(
            agree__lending__summary__director__department=user_department
        )  # 项目经理部门与用户所属部门相同项目
        return notify_list
    elif '项目经理' in job_list:
        notify_list = notify_list.filter(
            Q(agree__lending__summary__director=request_user) |
            Q(agree__lending__summary__assistant=request_user))  # 用户为项目经理或助理项目
        return notify_list
    else:
        return notify_list


# ---------------------------放款筛选函数----------------------------#
def provide_list_screen(provide_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        provide_list = provide_list.filter(
            notify__agree__lending__summary__director__department=
            user_department)  # 项目经理部门与用户所属部门相同项目
        return provide_list
    elif '项目经理' in job_list:
        provide_list = provide_list.filter(
            Q(notify__agree__lending__summary__director=request_user)
            | Q(notify__agree__lending__summary__assistant=request_user)
        )  # 用户为项目经理或助理项目
        return provide_list
    else:
        return provide_list


# ---------------------------客户筛选函数----------------------------#
def custom_list_screen(custom_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        custom_list = custom_list.filter(
            managementor__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return custom_list
    elif '项目经理' in job_list:
        custom_list = custom_list.filter(
            managementor=request_user)  # 用户为项目经理或助理项目
        return custom_list
    else:
        return custom_list

# ---------------------------保后客户筛选函数----------------------------#
def review_custom_list_screen(custom_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        custom_list = custom_list.filter(
            managementor__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return custom_list
    elif '项目经理' in job_list:
        custom_list = custom_list.filter(
            managementor=request_user)  # 用户为项目经理或助理项目
        return custom_list
    elif '风控专员' in job_list and not '保后管理岗' in job_list:
        custom_list = custom_list.filter(
            controler=request_user)  # 用户为项目经理或助理项目
        return custom_list
    else:
        return custom_list




# ---------------------------权证筛选函数----------------------------#
def warrant_list_screen(warrant_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(
            employee_department=request_user)  # 用户所属部门
        warrant_list = warrant_list.filter(
            warrant_buildor__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return warrant_list
    elif '项目经理' in job_list:
        warrant_list = warrant_list.filter(
            warrant_buildor=request_user)  # 用户为项目经理或助理项目
        return warrant_list
    else:
        return warrant_list


# ---------------------------项目访问权限----------------------------#
def article_right(func):  # 项目权限控制
    def inner(request, *args, **kwargs):
        article_obj = models.Articles.objects.get(
            id=kwargs['article_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        article_manager_department = article_obj.director.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(
            employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee=article_obj)
                | Q(assistant_employee=article_obj)).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该项目的项目经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------合同访问权限----------------------------#
def agree_right(func):  # 合同权限控制
    def inner(request, *args, **kwargs):
        agree_obj = models.Agrees.objects.get(id=kwargs['agree_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        article_manager_department = agree_obj.lending.summary.director.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(
            employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee__lending_summary__agree_lending=agree_obj)
                |
                Q(assistant_employee__lending_summary__agree_lending=agree_obj)
            ).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该项目的项目经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------放款通知访问权限----------------------------#
def notify_right(func):  # 合同权限控制
    def inner(request, *args, **kwargs):
        notify_obj = models.Notify.objects.get(id=kwargs['notify_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        article_manager_department = notify_obj.agree.lending.summary.director.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(
            employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee__lending_summary__agree_lending__notify_agree
                  =notify_obj) |
                Q(assistant_employee__lending_summary__agree_lending__notify_agree
                  =notify_obj)).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该项目的项目经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------放款访问权限----------------------------#
def provide_right(func):  # 合同权限控制
    def inner(request, *args, **kwargs):
        provide_obj = models.Provides.objects.get(
            id=kwargs['provide_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        article_manager_department = provide_obj.notify.agree.lending.summary.director.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(
            employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee__lending_summary__agree_lending__provide_notify
                  =provide_obj) |
                Q(assistant_employee__lending_summary__agree_lending__provide_notify
                  =provide_obj)).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该项目的项目经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------客户访问权限----------------------------#
def custom_right(func):  # 项目权限控制
    def inner(request, *args, **kwargs):
        custom_obj = models.Customes.objects.get(id=kwargs['custom_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        custom_managementor_department = custom_obj.managementor.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(
            employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not custom_managementor_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该客户不归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(manage_employee=custom_obj)
                | Q(manage_employee=custom_obj)).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该客户的管护经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------权证访问权限----------------------------#
def warrant_right(func):  # 权证访问权限
    def inner(request, *args, **kwargs):
        warrant_obj = models.Warrants.objects.get(
            id=kwargs['warrant_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        warrant_manager_department = warrant_obj.warrant_buildor.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(
            employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not warrant_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                warrant_buildor_employee=warrant_obj).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该项目的项目经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------功能权限----------------------------#
def authority(func):  # 权限控制
    def inner(request, *args, **kwargs):
        current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
        authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
        # today_stamp = time.mktime(datetime.date.today())  # 元组转换为时间戳
        limit_date = '2021-12-31'
        limit_date_tup = time.strptime(limit_date, "%Y-%m-%d")  # 字符串转换为元组
        limit_date_stamp = time.mktime(limit_date_tup)  # 元组转换为时间戳

        today_str = str(datetime.date.today())  # 元组转换为字符串
        today_tup = time.strptime(today_str, "%Y-%m-%d")  # 字符串转换为元组
        today_stamp = time.mktime(today_tup)  # 元组转换为时间戳
        if not current_url_name in authority_list:
            response = {'status': True, 'message': None}
            response['status'] = False
            response['message'] = '无权限(%s)，请联系管理员！' % current_url_name
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
        elif today_stamp > limit_date_stamp:
            response = {'status': True, 'message': None}
            response['status'] = False
            response['message'] = ''
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
        # print(request.user, '>', request.path, '>', resolve(request.path).url_name, '>', request.POST, request.GET)
        return func(request, *args, **kwargs)

    return inner


# ---------------------------项目流程权限----------------------------#
def sub_article_right(func):
    def inner(request, *args, **kwargs):
        response = {
            'status': True,
            'message': None,
            'forme': None,
        }
        post_data_str = request.POST.get('postDataStr')
        post_data = json.loads(post_data_str)
        article_id = post_data['article_id']
        article_obj = models.Articles.objects.get(id=article_id)  # 项目
        currentor = article_obj.currentor  # 项目当前审批人
        if not currentor == request.user:  # 登陆用户不是当前审批人
            response['status'] = False
            response['message'] = '你不是当前审批人，无权提交项目审批！'
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
        return func(request, *args, **kwargs)

    return inner


@login_required
# @authority
def home(request):
    # print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    # print('request.path_info', request.path_info)  # 当前url
    # print('request.path:', request.path)
    # print('resolve(request.path):', resolve(request.path))  # 路径转换为url_name等
    # print('resolve(request.path):', resolve(request.path).url_name)  # 路径转换为url_name、app_name
    # print('reverse(request.path):', reverse('home'))  # 将路径名转换为路径
    # print('request.get_host:', request.get_host())
    # print('request.GET.items():', request.GET.items())  # 获取get传递的参数对
    # print('acc_login-->request.COOKIES:', request.COOKIES)
    # print('acc_login-->request.session:', request.session)
    # print('acc_login-->request.GET:', request.GET)
    # print("request.session.get('authority_list'):", request.session.get('authority_list'))
    # print("request.session.get('menu_leaf_list'):", request.session.get('menu_leaf_list'))
    # lending_list = models.LendingOrder.objects.all()
    # for lending in lending_list:
    #     '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
    #                       (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    #     if lending.summary.article_state in [5, 51, 52, 55] and lending.lending_state == 4:
    #         models.LendingOrder.objects.filter(id=lending.id).update(lending_state=5)

    custom_list = models.Customes.objects.all()
    for custom in custom_list:
        custom_provide_balance_all = models.Provides.objects.filter(
            notify__agree__lending__summary__custom=custom).aggregate(
                Sum('provide_balance'))['provide_balance__sum']  # 客户项下，在保余额
        custom_ll = models.Customes.objects.filter(id=custom.id)
        if custom_provide_balance_all:
            custom_ll.update(amount=round(custom_provide_balance_all, 2))
        else:
            custom_ll.update(amount=0)
        rr = radio(custom.credit_amount, custom.g_value)
        vv = radio(custom.amount, custom.g_value)
        custom_ll.update(g_radio=rr, v_radio=vv)
    branch_list = models.Branches.objects.all()
    for branch_obj in branch_list:
        branch_provide_balance_all = models.Provides.objects.filter(
            notify__agree__branch=branch_obj).aggregate(
                Sum('provide_balance'))['provide_balance__sum']  # 放款银行项下，在保余额
        branch_ll = models.Branches.objects.filter(id=branch_obj.id)
        if branch_provide_balance_all:
            branch_ll.update(amount=round(branch_provide_balance_all, 2))
        else:
            branch_ll.update(amount=0)

    cooperator_list = models.Cooperators.objects.all()
    for cooperator_obj in cooperator_list:
        cooperator_provide_balance_all = models.Provides.objects.filter(
            notify__agree__branch__cooperator=cooperator_obj).aggregate(
                Sum('provide_balance'))['provide_balance__sum']  # 授信银行项下，在保余额
        cooperator_ll = models.Cooperators.objects.filter(id=cooperator_obj.id)
        if cooperator_provide_balance_all:
            cooperator_ll.update(
                amount=round(cooperator_provide_balance_all, 2))
        else:
            cooperator_ll.update(amount=0)

    dun_list = models.Dun.objects.all().order_by('-up_date')
    for dun_obj in dun_list:
        newest_ledge_obj = dun_obj.standing_dun.first()
        dun_list_l = models.Dun.objects.filter(id=dun_obj.id)
        if newest_ledge_obj:
            dun_list_l.update(up_date=newest_ledge_obj.standingor_date)

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


# -------------------------合同期限-------------------------#
def credit_term_c(credit_term):
    credit_term_exactly = credit_term % 12
    credit_term_cn = ''
    if credit_term_exactly == 0:
        credit_term_cn = '%s年' % convert_num(credit_term / 12)
    else:
        credit_term_cn = '%s个月' % convert_num(credit_term)
    return credit_term_cn


# -----------------------------金额小写转大写------------------------------#
def convert(n):
    units = ['', '万', '亿']
    nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    decimal_label = ['角', '分']
    small_int_label = ['', '拾', '佰', '仟']
    int_part, decimal_part = str(int(n)), str(round(n - int(n),
                                                    2))[2:]  # 分离整数和小数部分
    res = []
    if decimal_part:
        res.append(''.join([
            nums[int(x)] + y for x, y in list(zip(decimal_part, decimal_label))
            if x != '0'
        ]))
    if int_part != '0':
        res.append('圆')
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join([
                nums[int(x)] + (y if x != '0' else '') for x, y in list(
                    zip(small_int_part[::-1], small_int_label))[::-1]
            ])
            tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    result = ''.join(res[::-1])
    # print('len(result):',len(result),result,result[-1])
    if not result[-1] == '分':
        result += '整'
    return result


# -----------------------------数字小写转大写（含小数点）------------------------------#
def convert_num(n):
    units = ['', '万', '亿']
    nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    decimal_label = ['角', '分']
    small_int_label = ['', '拾', '佰', '仟']
    int_part, decimal_part = str(int(n)), str(round(n - int(n),
                                                    4))[2:]  # 分离整数和小数部分
    res = []
    if decimal_part:
        res.append(''.join(
            [nums[int(x)] for x in list(decimal_part) if x != '0']))

    if int_part != '0':
        if decimal_part and decimal_part != '0':
            res.append('点')
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join([
                nums[int(x)] + (y if x != '0' else '') for x, y in list(
                    zip(small_int_part[::-1], small_int_label))[::-1]
            ])
            tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    else:
        if decimal_part != 0:
            res.append('点')
            res.append('零')
    result = ''.join(res[::-1])
    # print('len(result):',len(result),result,result[-1])
    return result


# -----------------------------数字小写转大写（含小数点）------------------------------#
def convert_num_4(n):
    units = ['', '万', '亿']
    nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    decimal_label = ['角', '分']
    small_int_label = ['', '拾', '佰', '仟']
    int_part, decimal_part = str(int(n)), str(round(n - int(n),
                                                    4))[2:]  # 分离整数和小数部分
    res = []
    if decimal_part:
        res.append(''.join([nums[int(x)] for x in list(decimal_part)]))

    if int_part != '0':
        if decimal_part and decimal_part != '0':
            res.append('点')
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join([
                nums[int(x)] + (y if x != '0' else '') for x, y in list(
                    zip(small_int_part[::-1], small_int_label))[::-1]
            ])
            tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    else:
        if decimal_part != 0:
            res.append('点')
            res.append('零')
    result = ''.join(res[::-1])
    # print('len(result):',len(result),result,result[-1])
    return result


# -----------------------阿拉伯数字转换-------------------------#


def convert_str(n):
    units = ['', '万', '亿']
    nums = ['0', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    small_int_label = ['', '十', '百', '千']
    int_part, decimal_part = str(int(n)), str(round(n - int(n),
                                                    2))[2:]  # 分离整数和小数部分
    res = []
    if int_part != '0':
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join([
                nums[int(x)] + (y if x != '0' else '') for x, y in list(
                    zip(small_int_part[::-1], small_int_label))[::-1]
            ])
            tmp = tmp.rstrip('0').replace('000', '0').replace('00', '0')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    result = ''.join(res[::-1])
    if len(result) == 3:
        if result[0] == '一':
            result_l = result[1] + result[2]
            result = result_l
    elif len(result) == 2:
        if result[0] == '一':
            result_l = result[1]
            result = result_l
    return result


def un_dex(agree_typ):
    AGREE_TYP_D = models.Agrees.AGREE_TYP_D
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X
    if agree_typ in AGREE_TYP_D:
        un = '成都武侯中小企业融资担保有限责任公司'
        add = '成都市武侯区武青南路33号(武侯新城管委会内)'
        cnb = '028-85566171'
    elif agree_typ in AGREE_TYP_X:
        un = '成都武侯武兴小额贷款有限责任公司'
        add = '成都市武侯区武科西五路360号西部智谷B区2栋3单元10楼'
        cnb = '028-85566171'
    return (un, add, cnb)


def amount_s(amount):
    amount_str = str(round(amount / 10000,
                           6)).rstrip('0').rstrip('.')  # 总额（万元）
    return amount_str


def amount_y(amount):
    amount_str = str(round(amount, 2)).rstrip('0').rstrip('.')  # 总额（元）
    return amount_str


def radio(credit_amount: float, g_value: float):
    if credit_amount and credit_amount > 0:
        redioer = round(g_value / credit_amount * 100, 2)
    else:
        redioer = 0
    return redioer


def mc(v_start_date, v_end_date):
    v_year_end = v_end_date.year
    v_month_end = v_end_date.month
    v_year_start = v_start_date.year
    v_month_start = v_start_date.month
    interval = (v_year_end - v_year_start) * 12 + (v_month_end - v_month_start)
    return interval


def epi(provide_obj):  #还款计划
    provide_agree_obj = provide_obj.notify.agree
    provide_amount = provide_obj.provide_money  #放款金额
    repay_method = provide_agree_obj.repay_method  #还款方式
    try:
        agree_rate = float(provide_agree_obj.agree_rate) / 1000  #小贷月利率
        agree_rate_day = agree_rate / 30  #小贷日月利率
    except ValueError:
        agree_rate = 0.01
        agree_rate_day = 0.001
    inst_repay_prin_list = provide_obj.track_provide.filter(
        track_typ=21)  #分期还本列表
    inst_repay_prin_amt = inst_repay_prin_list.aggregate(
        Sum('term_pri'))['term_pri__sum']  #分期还款总额额
    if inst_repay_prin_amt:
        de_repay_prin = round(provide_amount - inst_repay_prin_amt,
                              2)  #扣除分期还款后的余额
    else:
        de_repay_prin = provide_amount
    provide_start_date = provide_obj.provide_date  #起始日
    provide_due_date = provide_obj.due_date  #到期日
    provide_term = mc(provide_start_date, provide_due_date)  #借款期数（月）
    if provide_term < 1:  #贷款期限不跨月
        provide_term_for = 1
    else:
        provide_term_for = provide_term
    start_date_er = datetime.date(provide_start_date.year,
                                  provide_start_date.month, 20)  #放款月20日
    start_date_er_dif = (start_date_er -
                         provide_start_date).days  #放款当月20日与放款日天差
    due_date_er = datetime.date(provide_due_date.year, provide_due_date.month,
                                20)  #到期月20日
    due_date_er_dif = (due_date_er - provide_due_date).days  #到期日与到期当月20日比较
    kkkk = []
    prin = provide_amount  #剩余本金
    term_int_j = prin
    total_int = 0.0  #利息累计
    total_prin = 0.0  #本金累计
    if repay_method == 21:  #等额本息
        term_amt = round(
            (provide_amount * (agree_rate) * (1 + agree_rate)**provide_term) /
            ((1 + agree_rate)**provide_term - 1), 2)  #每期还款额
        for i in range(1, provide_term + 1):
            term_int = round(prin * agree_rate, 2)  # 当期利息：上一期本金*利率
            term_prin = round(term_amt - term_int, 2)  #当期本金 = 每期还款额 - 当期利息
            if i == provide_term:
                term_prin = prin  #当期本金 = 剩余本金
                term_int = round(term_amt - term_prin, 2)
            term_amt = round(term_prin + term_int, 2)  #当期本息合计
            prin = round(prin - term_prin, 2)  # 剩余本金=上期剩余本金-当期还本金
            total_int = round(total_int + term_int, 2)  #利息累计
            total_prin = round(total_prin + term_prin, 2)  #本金累计
            ddd = provide_start_date + relativedelta(months=i)  #还款月
            if i == 1:
                pro_aft_dif = (ddd - provide_start_date).days
                kkkk.append({
                    'ddd_pro': provide_start_date,
                    'ddd_aft': ddd,
                    'pro_aft_dif': pro_aft_dif,
                    'term_int': term_int,
                    'term_prin': term_prin,
                    'term_amt': term_amt,
                    'total_int': total_int,
                    'prin': prin,
                    'term_int_j': term_int_j,
                    'track_typ': 25,
                })
            else:
                pro_aft_dif = (ddd - ddd_pro).days
                kkkk.append({
                    'ddd_pro': ddd_pro,
                    'ddd_aft': ddd,
                    'pro_aft_dif': pro_aft_dif,
                    'term_int': term_int,
                    'term_prin': term_prin,
                    'term_amt': term_amt,
                    'total_int': total_int,
                    'prin': prin,
                    'term_int_j': term_int_j,
                    'track_typ': 25,
                })
            ddd_pro = ddd
            term_int_j = prin
    elif repay_method == 11 or repay_method == 31:  #按月付息，到期还本
        iiii = []  #分期还本列表
        for inst_repay_prin in inst_repay_prin_list:
            iiii.append({
                'ddd_aft': inst_repay_prin.plan_date,
                'term_prin': inst_repay_prin.term_pri,
                'track_typ': inst_repay_prin.track_typ,
            })

        pppp = []  #按月付息列表
        for i in range(1, provide_term_for + 1):
            ddd = provide_start_date + relativedelta(months=i)  #还款月
            ddd_er = datetime.date(ddd.year, ddd.month, 20)  #还款月20日
            if start_date_er_dif > 0:  #如果放款在当月20日之前（当月20日要收息）
                i += 1
                if i == 2:
                    pppp.append({
                        'ddd_aft': start_date_er,
                        'term_prin': 0,
                        'track_typ': 31,
                    })  #当月20日
                    if provide_term_for == 1:  # 一共只有一期，跨月
                        if due_date_er_dif < 0:  #如果到期在当月20日之后
                            pppp.append({
                                'ddd_aft': ddd_er,
                                'term_prin': 0,
                                'track_typ': 31,
                            })
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                    else:
                        pppp.append({
                            'ddd_aft': ddd_er,
                            'term_prin': 0,
                            'track_typ': 31,
                        })  #放款第2月20日
                elif i == (provide_term_for + 1):  #最后一期
                    if due_date_er_dif >= 0:  #如果到期在当月20日之前
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                    else:
                        pppp.append({
                            'ddd_aft': ddd_er,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                else:
                    pppp.append({
                        'ddd_aft': ddd_er,
                        'term_prin': 0,
                        'track_typ': 31,
                    })
            else:  #如果放款在当月20日之之后（当月20日不收息）
                if i == 1:
                    if provide_term == 0:  #一共只有一期，不跨月
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                    elif provide_term == 1:  #一共只有一期，跨月
                        if due_date_er_dif < 0:  #如果到期在当月20日之后
                            pppp.append({
                                'ddd_aft': ddd_er,
                                'term_prin': 0,
                                'track_typ': 31,
                            })
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                    else:
                        pppp.append({
                            'ddd_aft': ddd_er,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                elif i == (provide_term_for):  #最后一期
                    if due_date_er_dif >= 0:  #如果到期在当月20日之前
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                    else:
                        pppp.append({
                            'ddd_aft': ddd_er,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                        pppp.append({
                            'ddd_aft': provide_due_date,
                            'term_prin': 0,
                            'track_typ': 31,
                        })
                else:
                    pppp.append({
                        'ddd_aft': ddd_er,
                        'term_prin': 0,
                        'track_typ': 31,
                    })

        iipp = []  #分期还本与按月付息合并
        ddd_pro = provide_start_date  #计息起始日
        term_int_p = provide_amount  #本期计息额
        for pp in pppp:
            ddd_aft_pp = pp['ddd_aft']
            term_int_j = 0  #本期计息额
            term_pri_p = 0  #本期还本额
            track_typ = pp['track_typ']
            for ii in iiii:
                ddd_aft_ii = ii['ddd_aft']
                ddd_aft_ip_dif = (ddd_aft_ii - ddd_aft_pp).days  #分期还款日与计息日比较
                ddd_pro_ip_dif = (ddd_aft_ii - ddd_pro).days  #分期还款日与起息日比较
                if ddd_aft_ip_dif < 0 and ddd_pro_ip_dif > 0:  #分期还款日在起息日与计息日之间
                    prin = prin - ii['term_prin']  #剩余本金
                    iipp.append({
                        'ddd_pro': ddd_pro,
                        'ddd_aft': ii['ddd_aft'],
                        'term_prin': ii['term_prin'],
                        'track_typ': ii['track_typ'],
                        'term_int_j': ii['term_prin'],
                        'prin': prin,
                    })
                    ddd_pro = ii['ddd_aft']
                    term_int_p = prin
                elif ddd_aft_ip_dif == 0:  #分期还款日与计息日为同一天
                    term_int_p = prin
                    term_pri_p = pp['term_prin'] + ii['term_prin']
                    prin = prin - term_pri_p  #剩余本金
                    track_typ = ii['track_typ']
            term_int_j = term_int_p  #当期计息额
            iipp.append({
                'ddd_pro': ddd_pro,
                'ddd_aft': pp['ddd_aft'],
                'term_prin': term_pri_p,
                'track_typ': track_typ,
                'term_int_j': term_int_j,
                'prin': prin,
            })
            ddd_pro = pp['ddd_aft']
            term_int_p = prin
        iipp_len = len(iipp)
        iipp_len_i = 0
        for iip in iipp:
            iipp_len_i += 1
            term_amt = 0  #本息合计
            ddd_pro = iip['ddd_pro']  #起息日
            ddd_aft = iip['ddd_aft']  #计息日
            term_prin = iip['term_prin']
            term_int_j = iip['term_int_j']  #计息日本金
            pro_aft_dif = (ddd_aft - ddd_pro).days  #计息天数
            term_int = round(term_int_j * agree_rate_day * pro_aft_dif,
                             2)  #当期利息
            total_int = round(total_int + term_int, 2)  #利息累计
            if iipp_len_i == iipp_len:
                term_prin = de_repay_prin
                prin = round(iip['prin'] - term_prin, 2)
            else:
                prin = iip['prin']
            term_amt = round(term_prin + term_int, 2)

            kkkk.append({
                'ddd_pro': ddd_pro,
                'ddd_aft': ddd_aft,
                'pro_aft_dif': pro_aft_dif,
                'term_int': term_int,
                'term_prin': term_prin,
                'term_amt': term_amt,
                'total_int': total_int,
                'prin': prin,
                'term_int_j': term_int_j,
                'track_typ': iip['track_typ'],
            })
    return kkkk


def provide_update(provide_obj: object, response: dict):
    provide_list = models.Provides.objects.filter(id=provide_obj.id)
    '''provide_repayment_sum，更新放款还款情况'''
    provide_repayment_amount = models.Repayments.objects.filter(
        provide=provide_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']  # 放款项下还款合计
    provide_balance = round(provide_obj.provide_money -
                            provide_repayment_amount, 2)  # 在保余额
    provide_list.update(provide_repayment_sum=round(provide_repayment_amount,
                                                    2),
                        provide_balance=provide_balance)  # 放款，更新还款总额，在保余额
    if provide_balance == 0:  # 在保余额为0
        '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
        provide_list.update(provide_status=11)  # 放款解保
        response['message'] = '成功还款,本次放款已全部结清！'
    else:
        response['message'] = '成功还款！'
    '''notify_repayment_sum，更新放款通知还款情况'''
    notify_list = models.Notify.objects.filter(
        provide_notify=provide_obj)  # 放款通知
    notify_obj = notify_list.first()
    notify_repayment_amount = models.Repayments.objects.filter(
        provide__notify=notify_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
    notify_provide_balance = models.Provides.objects.filter(
        notify=notify_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 通知项下在保合计
    notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2),
                       notify_balance=round(notify_provide_balance,
                                            2))  # 放款通知，更新还款总额
    '''agree_repayment_sum，更新合同还款信息'''
    agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
    agree_obj = agree_list.first()
    agree_repayment_amount = models.Repayments.objects.filter(
        provide__notify__agree=agree_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
    agree_provide_balance = models.Provides.objects.filter(
        notify__agree=agree_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保合计
    if round(agree_provide_balance) == 0:  # 在保余额为0
        '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'),
                        (99, '作废'))'''
        agree_list.update(
            agree_repayment_sum=round(agree_repayment_amount, 2),
            agree_balance=round(agree_provide_balance, 2),
            agree_state=61,
        )  # 合同，更新还款总额，在保余额，合同状态
        response['message'] = '成功还款,合同项下放款已全部结清，合同解保！'
    else:
        agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2),
                          agree_balance=round(agree_provide_balance, 2))
        # 合同，更新还款总额，在保余额
    '''lending_repayment_sum，更新放款次序还款信息'''
    lending_list = models.LendingOrder.objects.filter(
        agree_lending=agree_obj)  # 放款次序
    lending_obj = lending_list.first()
    lending_repayment_amount = models.Repayments.objects.filter(
        provide__notify__agree__lending=lending_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']
    lending_provide_balance = models.Provides.objects.filter(
        notify__agree__lending=lending_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']
    if round(lending_provide_balance) == 0:  # 在保余额为0
        '''LENDING_STATE = [(3, '待上会'), (4, '已上会'), (5, '已签批'),
                            (51, '已放款'), (52, '已放完'), (55, '已解保'), 
                            (61, '待变更'),(99, '已注销')]'''
        lending_list.update(lending_repayment_sum=round(
            lending_repayment_amount, 2),
                            lending_balance=round(lending_provide_balance, 2),
                            lending_state=55)  # 放款次序，更新还款总额
    else:
        lending_list.update(lending_repayment_sum=round(
            lending_repayment_amount, 2),
                            lending_balance=round(lending_provide_balance,
                                                  2))  # 放款次序，更新还款总额
    '''article_repayment_sum，更新项目还款信息'''
    article_list = models.Articles.objects.filter(
        lending_summary=lending_obj)  # 项目
    article_obj = article_list.first()
    article_repayment_amount = models.Repayments.objects.filter(
        provide__notify__agree__lending__summary=article_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']
    article_provide_balance = models.Provides.objects.filter(
        notify__agree__lending__summary=article_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']

    if round(article_provide_balance) == 0:  # 在保余额为0
        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), 
        (4, '已上会'), (5, '已签批'),(51, '已放款'), (52, '已放完'), (55, '已解保'),
        (61, '待变更'), (99, '已注销'))'''
        article_list.update(article_repayment_sum=round(
            article_repayment_amount, 2),
                            article_balance=round(article_provide_balance, 2),
                            article_state=55)  # 项目，更新还款总额
        response['message'] = '成功还款,项目项下放款已全部结清，项目解保！'
    else:
        article_list.update(article_repayment_sum=round(
            article_repayment_amount, 2),
                            article_balance=round(article_provide_balance,
                                                  2))  # 项目，更新还款总额
    '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
    custom_list = models.Customes.objects.filter(article_custom=article_obj)
    custom_obj = custom_list.first()
    branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
    branch_obj = branch_list.first()
    provide_typ = provide_obj.provide_typ
    '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'), (42, '小贷'))'''
    custom_provide_balance = models.Provides.objects.filter(
        notify__agree__lending__summary__custom=custom_obj,
        provide_typ=provide_typ).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 客户及放款品种项下，在保余额
    branch_provide_balance = models.Provides.objects.filter(
        notify__agree__branch=branch_obj, provide_typ=provide_typ).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    cooperator_list = models.Cooperators.objects.filter(
        branch_cooperator=branch_obj)
    cooperator_obj = cooperator_list.first()
    cooperator_provide_balance = models.Provides.objects.filter(
        notify__agree__branch__cooperator=cooperator_obj,
        provide_typ=provide_typ).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 授信银行及放款品种项下，在保余额
    if provide_typ == 1:
        custom_list.update(custom_flow=custom_provide_balance)  # 客户，更新流贷余额
        branch_list.update(branch_flow=branch_provide_balance)  # 放款银行，更新流贷余额
        cooperator_list.update(
            cooperator_flow=round(cooperator_provide_balance, 2))
    elif provide_typ == 11:
        custom_list.update(custom_accept=custom_provide_balance)  # 客户，更新承兑余额
        branch_list.update(branch_accept=branch_provide_balance)  # 放款银行，更新承兑余额
        cooperator_list.update(
            cooperator_accept=round(cooperator_provide_balance, 2))
    elif provide_typ == 21:
        custom_list.update(custom_back=custom_provide_balance)  # 客户，更新保函余额
        branch_list.update(branch_back=branch_provide_balance)  # 放款银行，更新保函余额
        cooperator_list.update(
            cooperator_back=round(cooperator_provide_balance, 2))
    elif provide_typ == 31:
        custom_list.update(entrusted_loan=custom_provide_balance)  # 客户，更新委贷余额
        branch_list.update(
            entrusted_loan=branch_provide_balance)  # 放款银行，更新委贷余额
        cooperator_list.update(
            entrusted_loan=round(cooperator_provide_balance, 2))
    elif provide_typ == 41:
        custom_list.update(petty_loan=custom_provide_balance)  # 客户，更新小贷余额
        branch_list.update(petty_loan=branch_provide_balance)  # 放款银行，更新小贷余额
        cooperator_list.update(petty_loan=round(cooperator_provide_balance, 2))
    '''更新客户、放款银行、授信银行在保总额'''
    custom_provide_balance_all = models.Provides.objects.filter(
        notify__agree__lending__summary__custom=custom_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 客户项下，在保余额
    if not custom_provide_balance_all:
        custom_provide_balance_all = 0
    v_radio = radio(custom_provide_balance_all, custom_obj.g_value)
    custom_list.update(amount=round(custom_provide_balance_all, 2),
                       v_radio=v_radio)
    branch_provide_balance_all = models.Provides.objects.filter(
        notify__agree__branch=branch_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 放款银行项下，在保余额
    branch_list.update(amount=round(branch_provide_balance_all, 2))
    cooperator_provide_balance_all = models.Provides.objects.filter(
        notify__agree__branch__cooperator=cooperator_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 授信银行项下，在保余额
    cooperator_list.update(amount=round(cooperator_provide_balance_all, 2))

    return response