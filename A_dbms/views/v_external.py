from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.db import transaction
from django.db.models import Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority

# -----------------------合作机构-------------------------#
@login_required
def cooperative(request, *args, **kwargs):  # 合作机构
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '合作机构'

    COOPERATOR_STATE_LIST = models.Cooperators.COOPERATOR_STATE_LIST
    cooperator_list = models.Cooperators.objects.filter(**kwargs).order_by('-flow_credit', '-flow_limit')

    ####分页信息###
    paginator = Paginator(cooperator_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/external/cooperative.html', locals())


# -----------------------即将到期合作协议-------------------------#
@login_required
def soondue_cooperator(request, *args, **kwargs):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '即将到期协议'

    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    soondue_cooperator_list = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__gte=datetime.date.today(), due_date__lt=date_th_later)  # 30天内到期协议
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['draft_num', 'draft_acceptor',
                         'draft__draft_owner__name', 'draft__draft_owner__short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        soondue_cooperator_list = soondue_cooperator_list.filter(q)

    provide_acount = soondue_cooperator_list.count()
    '''分页'''
    paginator = Paginator(soondue_cooperator_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/external/cooperative.html', locals())


# -----------------------逾期合作协议-------------------------#
@login_required
def overdue_cooperator(request, *args, **kwargs):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '逾期协议'

    overdue_cooperator_list = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__lt=datetime.date.today())  # 逾期协议
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['draft_num', 'draft_acceptor',
                         'draft__draft_owner__name', 'draft__draft_owner__short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        overdue_cooperator_list = overdue_cooperator_list.filter(q)

    provide_acount = overdue_cooperator_list.count()
    '''分页'''
    paginator = Paginator(overdue_cooperator_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/external/cooperative.html', locals())