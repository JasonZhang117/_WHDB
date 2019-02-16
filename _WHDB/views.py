from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models


def acc_login(request):
    '''
    :param request:
    :return:
    '''
    print(__file__, '-->acc_login')
    print('acc_login-->request.COOKIES:', request.COOKIES)
    print('acc_login-->request.session:', request.session)
    print('acc_login-->request.GET:', request.GET)
    error_msg = ''
    if request.method == "POST":
        print('request.POST.get:', request.POST.get)
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print("acc_login-->request.POST.get('username'):", username)
        print("acc_login-->request.POST.get('password'):", password)
        print("acc_login-->request.POST.get('code'):", code)
        user = authenticate(username=username, password=password)
        if user:
            menu_list = models.Menus.objects.filter(jobs__employees=user).distinct().order_by(
                'ordery').values('name', 'url_name')
            print('menu_list:', menu_list)
            request.session['menus'] = list(menu_list)
            authority_list = models.Authorities.objects.filter(
                jobs__employees=user).distinct().values('name', 'url_name')  # 权限列表
            request.session['authoritis'] = list(authority_list)
            carte_list = models.Cartes.objects.filter(
                authority_carte__jobs__employees=user).distinct().values('name', 'url_name')  # 菜单列表
            request.session['cartes'] = list(carte_list)
            job_list = models.Jobs.objects.filter(employees=user).values('name')  # 角色列表
            print('job_list:', job_list)
            request.session['jobs'] = list(job_list)

            # request.session['menus'] = [{'menu': '评审管理', 'url': 'dbms:article_all'},
            #                             {'menu': '个人主页', 'url': 'dbms:agree'}]
            login(request, user)
            return redirect(request.GET.get('next', 'dbms:index'))
        else:
            error_msg = "用户名或密码错误！"
    return render(request, 'login.html', {'error_msg': error_msg})
    # return render(request, 'dbms\login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    print(__file__, '---->def home')
    print('acc_login-->request.COOKIES:', request.COOKIES)
    print("acc_login-->request.user:", request.user)
    print('acc_login-->request.session:', request.session)
    print("acc_login-->request.session.get('menus'):", request.session.get('menus'))

    menu_list = models.Menus.objects.filter(jobs__employees=request.user).distinct().order_by(
        'ordery').values('name', 'url_name')  # 菜单列表
    authority_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().values('name', 'url_name')  # 权限列表
    carte_list = models.Cartes.objects.filter(
        authority_carte__jobs__employees=request.user).distinct().values('name', 'url_name')  # 菜单列表
    job_list = models.Jobs.objects.filter(employees=request.user).values('name')  # 角色列表

    menus_session = request.session.get('menus')  # 菜单
    authoritis_session = request.session.get('authoritis')  # 权限
    cartes_session = request.session.get('cartes')  # 菜单
    job_session = request.session.get('jobs')  # 菜单

    agree_list = models.Provides.objects.all()
    for agree in agree_list:
        agree_list_obj = models.Provides.objects.filter(id=agree.id)
    agree_obj = agree_list_obj.first()
    agree_amount = agree_obj.implement
    return render(request, 'index.html', locals())
