from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from .. import models, forms
import datetime, time, json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Avg, Min, Sum, Max, Count
from django.db import transaction
from django.urls import resolve
from _WHDB.views import (MenuHelper, authority, credit_term_c, convert, convert_num, un_dex, amount_s, amount_y,
                         agree_list_screen, agree_right)


# -----------------------部门列表-------------------------#
class Departments(View):  # 部门列表CBV
    def dispatch(self, request, *args, **kwargs):
        result = super(Departments, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        department_list = models.Departments.objects.all()
        return render(request,
                      'dbms/department/department.html',
                      locals())

    def post(self, request):
        ret = render(request,
                     'dbms/department/department.html',
                     locals())
        ret['h1'] = 'v1'  # 向响应头添加东东
        return ret


# -----------------------部门列表-------------------------#
@authority
def department(request):  # 部门列表
    department_list = models.Departments.objects.all()
    return render(request,
                  'dbms/department/department.html',
                  locals())


# -----------------------部门添加-------------------------#
@authority
def department_add(request):  # 部门添加
    if request.method == "GET":
        form = forms.DepartmentForm()
        return render(request,
                      'dbms/department/department-add.html',
                      locals())
    else:
        # form验证
        request_form_data = forms.DepartmentForm(
            request.POST, request.FILES)
        if request_form_data.is_valid():
            cleaned_form_data = request_form_data.cleaned_data
            models.Departments.objects.create(**cleaned_form_data)  # 添加数据库
            return redirect('dbms:department')
        else:
            return render(request,
                          'dbms/department/department-add.html',
                          locals())


# -----------------------部门添加-------------------------#
@authority
def department_edit(request, department_id):  # 部门添加
    if request.method == "GET":
        form_data = models.Departments.objects.get(id=department_id)
        # form初始化，适合做修改该
        form = forms.DepartmentForm({'name': form_data.name})
        return render(request,
                      'dbms/department/department-edit.html',
                      locals())
    else:
        # form验证
        form = forms.DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            # 修改数据库
            models.Customes.objects.get(id=department_id).update(**cleaned_form_data)
            return redirect('/dbms/department/')
        else:
            return render(request,
                          'dbms/department/department-edit.html',
                          locals())


# -----------------------部门删除-------------------------#
@authority
def department_del(request, department_id):  # 部门删除
    models.Departments.objects.get(id=department_id).delete()
    return redirect('dbms:department')


# -----------------------用户列表-------------------------#
@login_required
@authority
def employee(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '用户列表'
    EMPLOYEE_STATUS_LIST = models.Employees.EMPLOYEE_STATUS_LIST
    '''筛选'''
    employee_list = models.Employees.objects.filter(**kwargs).select_related('department', ).order_by('num')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['email', 'num', 'name', 'department__name', ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        employee_list = employee_list.filter(q)

    '''分页'''
    paginator = Paginator(employee_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/employee/employee.html', locals())


# -----------------------------查看用户------------------------------#
@login_required
@authority
def employee_scan(request, employee_id):  # 查看用户
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '用户详情'

    employee_list = models.Employees.objects.filter(id=employee_id)
    employee_obj = employee_list.first()

    return render(request, 'dbms/employee/employee-scan.html', locals())


# -----------------------------查看用户------------------------------#
@login_required
@authority
def employee_scan(request, employee_id):  # 查看用户
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '用户详情'

    employee_list = models.Employees.objects.filter(id=employee_id)
    employee_obj = employee_list.first()

    return render(request, 'dbms/employee/employee-scan.html', locals())


# ---------------------------重置密码ajax----------------------------#
@login_required
@authority
def employee_reset_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    employee_list = models.Employees.objects.filter(id=post_data['employee_id'])
    employee_obj = employee_list.first()
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    if employee_obj.employee_status in [1, 11]:
        try:
            with transaction.atomic():
                employee_list.update(
                    password='pbkdf2_sha256$120000$e8RCBOfbeyAx$4DRKCgNyJvD5FSn8jNM4QAV/5qn55RX2HMsLzZWx42k=', )
            response['skip'] = "/dbms/employee/scan/%s" % employee_obj.id
            response['message'] = '重置密码为：“%s”，请及时修改！' % 'WH666666'
        except Exception as e:
            response['status'] = False
            response['message'] = '重置密码失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '用户状态为：%s，重置密码失败！！！' % employee_obj.employee_status
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------员工编辑-------------------------#
def employee_edit(request, employee_id):  # 员工编辑
    if request.method == "GET":
        form_data = models.Employees.objects.get(id=employee_id)
        department = form_data.department.id
        print('form_data.department.id:', department)
        print('form_data.department.id:', type(department))
        job = form_data.job.values_list('id', 'name')
        print('form_data.job:', job)
        print('form_data.job:', type(job))
        # form初始化，适合做修改该
        data = {'user_id': form_data.user_id,
                'name': form_data.name,
                'id_code': form_data.id_code,
                'department': form_data.department.id,
                'job': [1, 3],
                'age': form_data.age,
                'e_mail': form_data.e_mail,
                'password': form_data.password,
                'status': form_data.status
                }
        form = forms.EmployeeForm(data)
        return render(request,
                      'dbms/employee/employee-edit.html',
                      locals())
    else:
        # form验证
        form = forms.EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            # 修改数据库

            models.Employees.objects.filter(
                id=employee_id).update(**cleaned_form_data)

            return redirect('/dbms/employee/')
        else:
            return render(request, 'dbms/employee/employee-edit.html', locals())


# -----------------------员工删除-------------------------#
def employee_del(request, employee_id):  # 员工删除
    print('-------------------employee_del----------------------------')
    employee_obj = models.Employees.objects.get(id=employee_id)
    print(employee_obj)
    employee_obj.delete()
    return redirect('/dbms/employee/')


# -----------------------员工删除ajax-------------------------#
def employee_del_ajax(request):  # 员工删除ajax
    nid = request.GET.get('nid')
    msg = '成功'
    try:
        models.Employees.objects.filter(id=nid).delete()
    except Exception as e:
        msg = str(e)
    return HttpResponse(msg)
