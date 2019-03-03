from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import datetime, time, re
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
    print('request.GET.items():', request.GET.items())  # 获取get传递的参数对

    print('acc_login-->request.COOKIES:', request.COOKIES)
    print('acc_login-->request.session:', request.session)
    print('acc_login-->request.GET:', request.GET)
    print("request.session.get('authoritis'):", request.session.get('authoritis'))
    print("request.session.get('cartes'):", request.session.get('cartes'))
    authority_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().order_by('ordery').values(
        'name', 'url_name', 'carte')  # 权限列表
    # [{'id': 2, 'name': '查看项目列表', 'url_name': 'dbms:article_all', 'carte': 1},]
    no_carte_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().filter(
        carte__isnull=True).values('name', 'url_name', 'carte')  # 无菜单权限列表

    # 获取菜单的叶子节点，即：菜单的最后一层应该显示的权限
    menu_leaf_list = list(models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().order_by('ordery').exclude(
        carte__isnull=True).values(
        'id', 'name', 'url', 'url_name', 'carte', 'ordery'))  # 有菜单权限列表
    current_url = request.path_info  # 访问的url
    current_url_name = resolve(request.path).url_name  # 访问的url
    menu_leaf_dict = {}  # 有菜单权限字典
    open_leaf_parent_id = None
    # 归并所有的叶子节点
    for item in menu_leaf_list:
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
        print(" item['url_name']:", item['url_name'], 'current_url_name:', current_url_name)
        if item['url_name'] == current_url_name:
            item['open'] = True
            open_leaf_parent_id = item['parent_id']

    # 获取所有菜单字典
    menu_list = list(models.Cartes.objects.filter(
        authority_carte__jobs__employees=request.user).distinct().order_by('ordery').values(
        'id', 'caption', 'parent_id', 'ordery'))  # # 获取所有的菜单列表
    '''将列表menu_list转换为字典，'''
    menu_dict = {}  # 菜单字典
    for item in menu_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
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

    result = []
    for row in menu_dict.values():
        if not row['parent_id']:
            result.append(row)
        else:
            menu_dict[row['parent_id']]['child'].append(row)
    print('menu_list:', menu_list)
    print('result:', result)

    return render(request, 'index.html', locals())
