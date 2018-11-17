from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models


# Create your views here.
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
            login(request, user)
            # request.user = user
            print("acc_login-->user:", user)
            print("acc_login-->user.name:", user.name)
            print("acc_login-->user.num:", user.num)
            return redirect(request.GET.get('next', 'home'),
                            usernum=user.num)
        else:
            error_msg = "Wrong username or password!"
    return render(request, 'login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    return redirect('login')


@login_required
def home(request, usernum):
    print(__file__, '---->def home')
    print("acc_login-->user:", usernum)
    print("acc_login-->request.user:", request.user)
    article_state_list = models.Articles.ARTICLE_STATE_LIST
    article_state_list_dic = list(map(
        lambda x: {'id': x[0], 'name': x[1]},
        article_state_list))
    print('acc_login-->article_state_list:', article_state_list)
    # 列表或元组转换为字典并添加key
    article_list = models.Articles.objects.all(). \
        select_related(
        'custom',
        'director',
        'assistant',
        'control')
    print('acc_login-->article_list:', article_list)
    return render(request, 'home.html', locals())
