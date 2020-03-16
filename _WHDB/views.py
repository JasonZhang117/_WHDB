from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import json, datetime, time, re
from django.urls import resolve, reverse
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.db import transaction

UND = '成都武侯中小企业融资担保有限责任公司'
UNX = '成都武侯武兴小额贷款有限责任公司'

FICATION_LIST = [(11, '正常'), (21, '关注'), (31, '次级'), (41, '可疑'), (51, '损失')]


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


# ---------------------------登陆函数----------------------------#
def acc_login(request):
    ''':param request::return:'''
    # print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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


# ---------------------------登出函数----------------------------#
def acc_logout(request):
    logout(request)
    return redirect('login')


# ---------------------------项目筛选函数----------------------------#
def article_list_screen(article_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(employee_department=request_user)  # 用户所属部门
        article_list = article_list.filter(director__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return article_list
    elif '项目经理' in job_list:
        article_list = article_list.filter(
            Q(director=request_user) |
            Q(assistant=request_user))  # 用户为项目经理或助理项目
        return article_list
    else:
        return article_list


# ---------------------------合同筛选函数----------------------------#
def agree_list_screen(agree_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(employee_department=request_user)  # 用户所属部门
        agree_list = agree_list.filter(lending__summary__director__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return agree_list
    elif '项目经理' in job_list:
        agree_list = agree_list.filter(
            Q(lending__summary__director=request_user) |
            Q(lending__summary__assistant=request_user))  # 用户为项目经理或助理项目
        return agree_list
    else:
        return agree_list


# ---------------------------放款通知筛选函数----------------------------#
def notify_list_screen(notify_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(employee_department=request_user)  # 用户所属部门
        notify_list = notify_list.filter(
            agree__lending__summary__director__department=user_department)  # 项目经理部门与用户所属部门相同项目
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
        user_department = models.Departments.objects.get(employee_department=request_user)  # 用户所属部门
        provide_list = provide_list.filter(
            notify__agree__lending__summary__director__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return provide_list
    elif '项目经理' in job_list:
        provide_list = provide_list.filter(
            Q(notify__agree__lending__summary__director=request_user) |
            Q(notify__agree__lending__summary__assistant=request_user))  # 用户为项目经理或助理项目
        return provide_list
    else:
        return provide_list


# ---------------------------客户筛选函数----------------------------#
def custom_list_screen(custom_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(employee_department=request_user)  # 用户所属部门
        custom_list = custom_list.filter(
            managementor__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return custom_list
    elif '项目经理' in job_list:
        custom_list = custom_list.filter(managementor=request_user)  # 用户为项目经理或助理项目
        return custom_list
    else:
        return custom_list


# ---------------------------权证筛选函数----------------------------#
def warrant_list_screen(warrant_list, request):  # 项目筛选
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    request_user = request.user
    if '业务部负责人' in job_list:  # 如果为业务部门负责人
        user_department = models.Departments.objects.get(employee_department=request_user)  # 用户所属部门
        warrant_list = warrant_list.filter(warrant_buildor__department=user_department)  # 项目经理部门与用户所属部门相同项目
        return warrant_list
    elif '项目经理' in job_list:
        warrant_list = warrant_list.filter(warrant_buildor=request_user)  # 用户为项目经理或助理项目
        return warrant_list
    else:
        return warrant_list


# ---------------------------项目访问权限----------------------------#
def article_right(func):  # 项目权限控制
    def inner(request, *args, **kwargs):
        article_obj = models.Articles.objects.get(id=kwargs['article_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        article_manager_department = article_obj.director.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee=article_obj) |
                Q(assistant_employee=article_obj)).distinct()  # 项目经理及助理列表
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
        user_department = models.Departments.objects.get(employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee__lending_summary__agree_lending=agree_obj) |
                Q(assistant_employee__lending_summary__agree_lending=agree_obj)).distinct()  # 项目经理及助理列表
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
        user_department = models.Departments.objects.get(employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee__lending_summary__agree_lending__notify_agree=notify_obj) |
                Q(assistant_employee__lending_summary__agree_lending__notify_agree=notify_obj)).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该项目的项目经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------放款访问权限----------------------------#
def provide_right(func):  # 合同权限控制
    def inner(request, *args, **kwargs):
        provide_obj = models.Provides.objects.get(id=kwargs['provide_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        article_manager_department = provide_obj.notify.agree.lending.summary.director.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not article_manager_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该项目部归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(director_employee__lending_summary__agree_lending__provide_notify=provide_obj) |
                Q(
                    assistant_employee__lending_summary__agree_lending__provide_notify=provide_obj)).distinct()  # 项目经理及助理列表
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
        user_department = models.Departments.objects.get(employee_department=request.user)
        if '业务部负责人' in job_list:  # 如果为业务部门负责人
            if not custom_managementor_department == user_department:  # 项目经理不属于部门负责人所属部门
                return HttpResponse('该客户不归属你部门，无权访问！')
        if '项目经理' in job_list:
            user_list = models.Employees.objects.filter(
                Q(manage_employee=custom_obj) |
                Q(manage_employee=custom_obj)).distinct()  # 项目经理及助理列表
            if not request.user in user_list:
                return HttpResponse('你不是该客户的管护经理或助理，无权访问！')
        return func(request, *args, **kwargs)

    return inner


# ---------------------------权证访问权限----------------------------#
def warrant_right(func):  # 权证访问权限
    def inner(request, *args, **kwargs):
        warrant_obj = models.Warrants.objects.get(id=kwargs['warrant_id'])  # 项目
        job_list = request.session.get('job_list')  # 获取当前用户的所有角色
        warrant_manager_department = warrant_obj.warrant_buildor.department  # 项目经理所属部门
        user_department = models.Departments.objects.get(employee_department=request.user)
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
        # print(request.user, '>', request.path, '>', resolve(request.path).url_name, '>', request.POST, request.GET)
        return func(request, *args, **kwargs)

    return inner


# ---------------------------项目流程权限----------------------------#
def sub_article_right(func):
    def inner(request, *args, **kwargs):
        response = {'status': True, 'message': None, 'forme': None, }
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
    custom_list = models.Customes.objects.filter(credit_amount__gt=0)
    for custom in custom_list:
        rr = radio(custom.credit_amount,custom.g_value)
        custom_ll = models.Customes.objects.filter(id=custom.id)
        custom_ll.update()

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
    int_part, decimal_part = str(int(n)), str(round(n - int(n), 2))[2:]  # 分离整数和小数部分
    res = []
    if decimal_part:
        res.append(''.join([nums[int(x)] + y for x, y in list(zip(decimal_part, decimal_label)) if x != '0']))
    if int_part != '0':
        res.append('圆')
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join(
                [nums[int(x)] + (y if x != '0' else '') for x, y in
                 list(zip(small_int_part[::-1], small_int_label))[::-1]])
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
    int_part, decimal_part = str(int(n)), str(round(n - int(n), 4))[2:]  # 分离整数和小数部分
    res = []
    if decimal_part:
        res.append(''.join([nums[int(x)] for x in list(decimal_part) if x != '0']))

    if int_part != '0':
        if decimal_part and decimal_part != '0':
            res.append('点')
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join(
                [nums[int(x)] + (y if x != '0' else '') for x, y in
                 list(zip(small_int_part[::-1], small_int_label))[::-1]])
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
    int_part, decimal_part = str(int(n)), str(round(n - int(n), 2))[2:]  # 分离整数和小数部分
    res = []
    if int_part != '0':
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join(
                [nums[int(x)] + (y if x != '0' else '') for x, y in
                 list(zip(small_int_part[::-1], small_int_label))[::-1]])
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
    amount_str = str(round(amount / 10000, 6)).rstrip('0').rstrip('.')  # 总额（万元）
    return amount_str


def amount_y(amount):
    amount_str = str(round(amount, 2)).rstrip('0').rstrip('.')  # 总额（元）
    return amount_str

def radio(credit_amount:float,g_value:float):
    if credit_amount > 0:
        redioer = round(g_value/credit_amount*100,2)
    else:
        redioer = 0
    return redioer