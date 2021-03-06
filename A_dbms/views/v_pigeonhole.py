from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import (authority, provide_list_screen, provide_right)


# -----------------------归档列表---------------------#
@login_required
@authority
def pigeonhole(request, *args, **kwargs):  # 归档
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '归档管理'
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '暂存风控'), (21, '已归档')]'''
    IMPLEMENT_LIST = models.Provides.IMPLEMENT_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(**kwargs).select_related('notify').order_by('-provide_date')
    provide_list = provide_list_screen(provide_list, request)
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name',
                         'notify__agree__lending__summary__custom__short_name',
                         'notify__agree__branch__name', 'notify__agree__branch__short_name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        provide_list = provide_list.filter(q)

    balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    provide_acount = provide_list.count()  # 信息数目
    '''分页'''
    paginator = Paginator(provide_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/pigeonhole/pigeonhole.html', locals())


# -----------------------------查看归档------------------------------#
@login_required
@authority
@provide_right
def pigeonhole_scan(request, provide_id):  # 查看放款
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '归档管理'

    provide_obj = models.Provides.objects.get(id=provide_id)
    form_implement_add = forms.FormImplementAdd()
    form_pigeonhole_add = forms.FormPigeonholeAdd()
    form_pigeonhole_num = forms.FormPigeonholeNumAdd()

    return render(request, 'dbms/pigeonhole/pigeonhole-scan.html', locals())


# -----------------------逾期归档---------------------#
@login_required
@authority
def pigeonhole_overdue(request, *args, **kwargs):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '逾期归档'

    date_15_leter = datetime.date.today() - datetime.timedelta(days=20)  # 15天前
    pigeonhole_overdue_list = models.Provides.objects.filter(
        implement__in=[1, 11, 21], provide_date__lt=date_15_leter).order_by('-provide_date')  # 逾期归档
    pigeonhole_overdue_list = provide_list_screen(pigeonhole_overdue_list, request)
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name',
                         'notify__agree__lending__summary__custom__short_name',
                         'notify__agree__branch__name', 'notify__agree__branch__short_name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        pigeonhole_overdue_list = pigeonhole_overdue_list.filter(q)

    balance = pigeonhole_overdue_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    provide_acount = pigeonhole_overdue_list.count()  # 信息数目

    '''分页'''
    paginator = Paginator(pigeonhole_overdue_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/pigeonhole/pigeonhole.html', locals())
