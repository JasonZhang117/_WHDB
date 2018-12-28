from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from .. import models
from .. import forms


# 部门、岗位、员工信息管理
# -----------------------部门管理-------------------------#
# -----------------------部门管理-------------------------#
# -----------------------部门管理-------------------------#
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
def department(request):  # 部门列表
    department_list = models.Departments.objects.all()
    return render(request,
                  'dbms/department/department.html',
                  locals())


# -----------------------部门添加-------------------------#
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
def department_del(request, department_id):  # 部门删除
    models.Departments.objects.get(id=department_id).delete()
    return redirect('dbms:department')


# -----------------------员工管理-------------------------#
# -----------------------员工管理-------------------------#
# -----------------------员工管理-------------------------#
# -----------------------员工列表-------------------------#
def employee(request):  # 员工列表
    print('-------------------employee----------------------------')
    employee_list = models.Employees.objects.filter(
        department__name='风控部', job__name='风控专员')
    # 一对多关系
    # 员工对应的部门（正向查询）
    department_obj = models.Employees.objects.filter(name='张建')[0].department
    print(department_obj)  # 通过对象
    department_obj = models.Departments.objects.filter(
        employee_department__name='张建')  # *****
    print(department_obj)  # 通过__
    # 风控部的员工(反向查询）
    department_obj = models.Departments.objects.filter(name='风控部')[0]
    employee_l = department_obj.employee_department.all()  # 反向查询
    print(employee_l)  # 通过对象
    employee_l = models.Employees.objects.filter(department__name='风控部')  # *****
    print(employee_l)  # 通过__
    employee_l = models.Departments.objects.filter(name='风控部').values(
        'employee_department__name')  # 反向查询
    print(employee_l)  # 通过__

    # 多对多关系
    # 员工对应的岗位（正向查找）
    employee_obj = models.Employees.objects.filter(name='孙祥')[0]
    print(employee_obj)
    job_l = employee_obj.job.all()
    print(job_l)
    job_l = models.Jobs.objects.filter(employee_job__name='孙祥')  # *****
    print(job_l)

    # 岗位对应的员工（反向查询）
    job_obj = models.Jobs.objects.filter(name='项目经理').first()
    print(job_obj)
    employee_l = job_obj.employee_job.all()
    print(employee_l)
    employee_l = models.Employees.objects.filter(job__name='项目经理')  # *****
    print(employee_l)

    # 通过对象绑定添加及删除
    employee_obj = models.Employees.objects.filter(name='孙祥')[0]
    job_l = models.Jobs.objects.all()
    # employee_job.add(**job_l)

    # 聚合查询aggregate
    from django.db.models import Avg, Min, Sum, Max, Count
    # 统计name字段的个数（风控部员工数）
    ret = models.Employees.objects.filter(job__name='风控专员').aggregate(Count('name'))
    print(ret)
    ret = models.Employees.objects.filter(job__name='风控专员').count()
    print(ret)
    # 分组查询annotate
    ret = models.Employees.objects.values('job__name')
    print(ret)
    ret = models.Employees.objects.values('job__name').annotate(Count('name'))
    print(ret)

    # F查询与Q查询
    # 查询部门为风控部且岗位为部门负责人
    ret = models.Employees.objects.filter(department__name='风控部',
                                          job__name='部门负责人')
    print(ret)
    from django.db.models import Q, F
    models.Employees.objects.all().update(age=F('age') + 1)  # 所有员工年龄加1
    ret = models.Employees.objects.filter(Q(department__name='风控部') |
                                          ~Q(job__name='部门负责人'))  # 或查询
    print(ret)
    ret = models.Employees.objects.filter(~Q(job__name='部门负责人'))  # 或查询
    print(ret)
    ret = models.Employees.objects.filter(job__name__contains='风')  # 或查询
    print(ret)
    # queryset 可迭代，可切片，有缓存（特性）
    if ret.exists():  # exists()方法确定queryset是否有值
        print(ret)
    ret = ret.iterator()  # 将查询结果转换为迭代器对象
    print(ret)
    for i in ret:
        print(i.id_code)
    add_link = 'dbms:employee_add'
    ajax_link = 'dbms:employee_add_ajax'

    # 跨表操作提交查询效率（ForeignKey，OneToOneField）
    Departments_name = models.Employees.objects.all(). \
        select_related('department_id')
    for row in Departments_name:
        print(row.name, row.department.name)
    print('Departments_name:', Departments_name)
    # 连表查询性能低
    Departments_name = models.Employees.objects.all(). \
        prefetch_related('department_id')
    # 进行两次查询

    return render(request, 'dbms/employee/employee.html', locals())


# -----------------------员工添加-------------------------#
def employee_add(request):  # 员工添加
    print('-------------------employee_add----------------------------')
    choices = [(1, '部门负责人'), (2, '项目经理'), (3, '风控专员')]
    print('choices:', choices)
    print(type(choices))
    Departments = models.Departments.objects.values_list('id', 'name')
    print('Departments:', Departments)
    print(type(Departments))
    Departments = tuple(models.Departments.objects.values_list('id', 'name'))
    print('Departments:', Departments)
    print(type(Departments))
    Departments = list(models.Departments.objects.values('id', 'name'))
    print('Departments:', Departments)
    print(type(Departments))
    Jobs = list(models.Jobs.objects.values_list('id', 'name').order_by('name'))
    print('Jobs:', Jobs)
    print(type(Jobs))
    if request.method == "GET":
        form = forms.EmployeeForm()
        return render(request, 'dbms/employee/employee-add.html', locals())
    else:
        # form验证
        print('request.POST:', request.POST)
        print(type(request.POST['age']))
        form = forms.EmployeeForm(request.POST, request.FILES)  # 验证form提交的数据
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            print('cleaned_form_data:', cleaned_form_data)
            department_id = int(cleaned_form_data['department'])
            department_obj = models.Departments.objects.get(pk=department_id)
            print('department_obj', department_obj)
            print(type(cleaned_form_data['department']))
            print(type(cleaned_form_data['job']))
            for i in list(cleaned_form_data['job']):
                print(type(i))
            status = cleaned_form_data['status']
            print('status:', type(status))
            # job_obj = models.Jobs.objects.get(pk=int(cleaned_form_data['job']))
            # print('job_obj', job_obj)
            employee_obj = models.Employees.objects.create(
                user_id=cleaned_form_data['user_id'],
                name=cleaned_form_data['name'],
                id_code=cleaned_form_data['id_code'],
                # department=department_obj,
                department_id=department_id,
                age=cleaned_form_data['age'],
                e_mail=cleaned_form_data['e_mail'],
                password=cleaned_form_data['password'],
                status=cleaned_form_data['status'])
            employee_obj.job.add(*cleaned_form_data['job'])  # 绑定多对多关系
            return redirect('dbms:employee')
        else:
            return render(request, 'dbms/employee/employee-add.html', locals())


# -----------------------员工编辑-------------------------#
def employee_edit(request, employee_id):  # 员工编辑
    print('-------------------employee_edit----------------------------')
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
    print('nid:', nid)
    msg = '成功'
    try:
        models.Employees.objects.filter(id=nid).delete()
    except Exception as e:
        msg = str(e)
    return HttpResponse(msg)
