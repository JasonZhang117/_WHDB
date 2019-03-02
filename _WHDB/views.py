from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import datetime, time
from django.urls import resolve, reverse


def acc_login(request):
    ''':param request::return:'''
    print(__file__, '-->acc_login')
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print("acc_login-->request.POST.get('username'):", username)
        print("acc_login-->request.POST.get('password'):", password)
        print("acc_login-->request.POST.get('code'):", code)
        user = authenticate(username=username, password=password)
        if user:
            '''查询菜单并写入session'''
            menu_list = models.Menus.objects.filter(jobs__employees=user).distinct().order_by(
                'ordery').values('name', 'url_name')
            request.session['menus'] = list(menu_list)
            '''查询权限并写入session'''
            authority_list = models.Authorities.objects.filter(
                jobs__employees=user).distinct().values('name', 'url_name', 'carte')  # 权限列表
            request.session['authoritis'] = list(authority_list)
            '''查询菜单本写入session'''
            yes_carte_list = models.Authorities.objects.filter(
                jobs__employees=user).distinct().exclude(
                carte__isnull=True).values('id', 'name', 'url_name', 'carte')  # 有菜单权限列表
            # [{'id': 2, 'name': '查看项目列表', 'url_name': 'dbms:article_all', 'carte': 1},]
            yes_carte_dict = {}  # 有菜单权限字典
            for item in yes_carte_list:
                item = {
                    'id': item['id'], 'url': item['url_name'], 'name': item['name'],
                    'parrent': item['carte'], 'child': []
                }  # 替换每个字典的键
                if item['parrent'] in yes_carte_dict:
                    yes_carte_dict[item['parrent']].append(item)
                else:
                    yes_carte_dict[item['parrent']] = [item, ]
            carte_list = models.Cartes.objects.filter(
                authority_carte__jobs__employees=user).distinct().values(
                'id', 'parrent', 'name', 'ordery').order_by('ordery')  # 菜单列表
            carte_dict = {}  # 菜单字典
            '''将列表carte_list转换为字典，'''
            for item in carte_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
                item['child'] = []  # 将每个字典添加一个child键，值设置为一个空列表
                carte_dict[item['id']] = item  # 将字典carte_dict键设为item字典的id值，值设为item字典
            for k, v in yes_carte_dict.items():
                carte_dict[k]['child'] = v  # 将权限挂到菜单上
            request.session['cartes'] = list(carte_list)
            '''查询角色并写入session'''
            job_list = models.Jobs.objects.filter(employees=user).values('name')  # 角色列表
            request.session['jobs'] = list(job_list)
            # request.session['menus'] = [{'menu': '评审管理', 'url': 'dbms:article_all'},
            #                             {'menu': '个人主页', 'url': 'dbms:agree'}]
            login(request, user)
            return redirect(request.GET.get('next', 'dbms:index'))
        else:
            error_msg = "用户名或密码错误！"
    return render(request, 'login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    print(__file__, '---->def home')
    print('request.path_info', request.path_info)  # 当前url
    print('request.path:', request.path)
    print('resolve(request.path):', resolve(request.path))  # 路径转换为url_name等
    print('resolve(request.path):', resolve(request.path).url_name)  # 路径转换为url_name、app_name
    print('reverse(request.path):', reverse('home'))  # 将路径名转换为路径
    print('request.get_host:', request.get_host())

    print('acc_login-->request.COOKIES:', request.COOKIES)
    print('acc_login-->request.session:', request.session)
    print('acc_login-->request.GET:', request.GET)
    print("request.session.get('authoritis'):", request.session.get('authoritis'))
    print("request.session.get('cartes'):", request.session.get('cartes'))
    authority_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().values('name', 'url_name', 'carte')  # 权限列表
    # [{'id': 2, 'name': '查看项目列表', 'url_name': 'dbms:article_all', 'carte': 1},]
    no_carte_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().filter(
        carte__isnull=True).values('name', 'url_name', 'carte')  # 无菜单权限列表
    # [{'id': 2, 'name': '查看项目列表', 'url_name': 'dbms:article_all', 'carte': 1},]
    yes_carte_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().exclude(
        carte__isnull=True).values('id', 'name', 'url_name', 'carte')  # 有菜单权限列表
    # [{'id': 2, 'name': '查看项目列表', 'url_name': 'dbms:article_all', 'carte': 1},]
    yes_carte_dict = {}  # 有菜单权限字典
    for item in yes_carte_list:
        item = {
            'id': item['id'],
            'url': item['url_name'],
            'name': item['name'],
            'parrent': item['carte'],
            'child': []
        }  # 替换每个字典的键
        if item['parrent'] in yes_carte_dict:
            yes_carte_dict[item['parrent']].append(item)
        else:
            yes_carte_dict[item['parrent']] = [item, ]
    print('yes_carte_dict:', yes_carte_dict)

    carte_list = models.Cartes.objects.filter(
        authority_carte__jobs__employees=request.user).distinct().values(
        'id', 'parrent', 'name', 'ordery')  # 菜单列表
    print('carte_list:', carte_list)
    carte_dict = {}  # 菜单字典
    '''将列表carte_list转换为字典，'''
    for item in carte_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
        item['child'] = []  # 将每个字典添加一个child键，值设置为一个空列表
        carte_dict[item['id']] = item  # 将字典carte_dict键设为item字典的id值，值设为item字典
    print('carte_dict:', carte_dict)
    for k, v in yes_carte_dict.items():
        carte_dict[k]['child'] = v  # 将权限挂到菜单上
    print('carte_list:', carte_list)
    print('list(carte_list):', list(carte_list))

    ''' [
            {'name': '项目管理', 'parrent': None, 'ordery': 1, 'chaild':[
                {'name': '评审管理', 'url': 'dbms/meeting/scan'},
                {'name': '评审管理', 'url': 'dbms/meeting/scan'},]},
            {'name': '评审管理', 'parrent': None, 'ordery': 2}
     ]'''
    result = []
    for row in carte_dict.values():
        if not row['parrent']:
            result.append(row)
        else:
            carte_dict[row['parrent']]['child'].append(row)
    print('result:', result)

    for item in result:
        print(item['name'])
        for r in item['child']:
            print('----', r['name'])
            for n in r['child']:
                print('-------->', n['name'])

    return render(request, 'index.html', locals())
