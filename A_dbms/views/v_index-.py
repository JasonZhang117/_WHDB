from django.shortcuts import render, redirect
from .. import models
from .. import forms


# 登陆、注册事务管理
# -----------------------登陆-------------------------#
# -----------------------登陆-------------------------#
# -----------------------登陆-------------------------#
def login(request):
    print("COOKIES:", request.COOKIES)
    print("SESSION:", request.session)
    if request.method == "POST":
        emplyee_obj = models.Employees.objects.all()
        print('emplyee_obj:', emplyee_obj)
        name = request.POST.get("user")
        pwd = request.POST.get("pwd")
        if name == 'yuan' and pwd == "123":
            # ret = redirect('dbms:index')
            # ret.set_cookie("username",{"11":"22"},max_age=10,
            #                expires=datetime.datetime.utcnow()+datetime.timedelta(days=3))
            # ret.set_cookie("username",{'11':'22','33':'44'},max_age=10)
            # return ret
            # COOKIE SESSION
            request.session["is_login"] = True
            request.session["user"] = name
            request.session["lllll"] = [1, 2, 3, 4, 5]
            request.session["ssss"] = {'ss': 'pp'}
            return redirect('dbms:index')
    return render(request, 'dbms/login.html')


# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
def index(request):
    print("COOKIES", request.COOKIES)
    print("COOKIES", request.session)
    print('request:', request)
    # name = "{'11': '22'}" #数据库拿
    name = request.session.get('user', None)
    # coo = request.COOKIES.get('usrname',None)
    coo = request.session.get('is_login', None)
    print('coo:', coo)
    lll = request.session.get('lllll', None)
    print('lll:', type(lll))
    sss = request.session.get('ssss', None)
    print('ssss:', type(sss))
    if coo:
        print('name:', name)
        return render(request, 'dbms/index.html', locals())
    else:
        return redirect('dbms:login')
