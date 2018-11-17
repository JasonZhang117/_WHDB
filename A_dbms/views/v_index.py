from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .. import models
from .. import forms


# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
@login_required
def index(request, usernum):
    '''
    初始化本人权限、菜单，显示本人待处理信息，
    显示本人业务统计信息
    :param request:
    :return:
    '''
    print('index-->request.user.job.all():', request.user.job.all())
    print(__file__, '-->index')
    print("index-->usernum:", usernum)
    print('index-->request.user:', request.user)
    return render(request, 'dbms/index.html', locals())
