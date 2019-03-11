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
@authority
def cooperative(request, *args, **kwargs):  # 合作机构
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '合作机构'

    COOPERATOR_TYPE_LIST = models.Cooperators.COOPERATOR_TYPE_LIST
    cooperator_list = models.Cooperators.objects.filter(**kwargs).order_by('-flow_credit', '-flow_limit')

    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name',  # 追偿项目编号
                         'short_name',  # 客户名称
                         ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        cooperator_list = cooperator_list.filter(q)

    flow_credit_amount = cooperator_list.aggregate(Sum('flow_credit'))['flow_credit__sum']  # 综合额度
    if flow_credit_amount:
        flow_credit_amount = round(flow_credit_amount, 2)
    else:
        flow_credit_amount = 0
    back_credit_amount = cooperator_list.aggregate(Sum('back_credit'))['back_credit__sum']  # 保函额度
    if back_credit_amount:
        back_credit_amount = round(back_credit_amount, 2)
    else:
        back_credit_amount = 0

    flow_amount = cooperator_list.aggregate(Sum('cooperator_flow'))['cooperator_flow__sum']  # 流贷余额
    accept_amount = cooperator_list.aggregate(Sum('cooperator_accept'))['cooperator_accept__sum']  # 承兑余额
    back_amount = cooperator_list.aggregate(Sum('cooperator_back'))['cooperator_back__sum']  # 保函余额
    if flow_amount:
        flow_amount = flow_amount
    else:
        flow_amount = 0
    if accept_amount:
        accept_amount = accept_amount
    else:
        accept_amount = 0
    if back_amount:
        back_amount = back_amount
    else:
        back_amount = 0
    balance = flow_amount + accept_amount + back_amount

    compensatory_amount = cooperator_list.count()  # 信息数目

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


# -----------------------------机构详情------------------------------#
@login_required
@authority
def cooperative_scan(request, cooperator_id):  # 查看放款
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '机构详情'

    cooperator_obj = models.Cooperators.objects.get(id=cooperator_id)

    today_str = datetime.date.today()
    form_agreement_data = {'credit_date': str(today_str), 'due_date': str(today_str + datetime.timedelta(days=365))}
    form_agreement_add = forms.FormAgreementAdd(initial=form_agreement_data)
    return render(request, 'dbms/external/cooperative-scan.html', locals())


# -----------------------即将到期合作协议-------------------------#
@login_required
@authority
def soondue_cooperator(request, *args, **kwargs):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '即将到期协议'

    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    soondue_cooperator_list = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__gte=datetime.date.today(),
        due_date__lt=date_th_later).order_by('-due_date')  # 30天内到期协议
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
@authority
def overdue_cooperator(request, *args, **kwargs):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '逾期协议'

    overdue_cooperator_list = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__lt=datetime.date.today()).order_by('-due_date')  # 逾期协议
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


# -----------------------放款机构-------------------------#
@login_required
@authority
def branches(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款机构'
    BRANCH_STATE_LIST = models.Branches.BRANCH_STATE_LIST
    branch_list = models.Branches.objects.filter(**kwargs).select_related(
        'cooperator').order_by('-branch_flow', '-branch_accept', '-branch_back')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['cooperator__name',  # 合作机构名称
                         'cooperator__short_name',  # 合作机构简称
                         'name',  # 放款机构名称
                         'short_name',  # 放款机构简称
                         ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        branch_list = branch_list.filter(q)

    flow_amount = branch_list.aggregate(Sum('branch_flow'))['branch_flow__sum']  # 流贷余额
    accept_amount = branch_list.aggregate(Sum('branch_accept'))['branch_accept__sum']  # 承兑余额
    back_amount = branch_list.aggregate(Sum('branch_back'))['branch_back__sum']  # 保函余额

    if flow_amount:
        flow_amount = flow_amount
    else:
        flow_amount = 0
    if accept_amount:
        accept_amount = accept_amount
    else:
        accept_amount = 0
    if back_amount:
        back_amount = back_amount
    else:
        back_amount = 0
    balance = flow_amount + accept_amount + back_amount

    compensatory_amount = branch_list.count()  # 信息数目

    ####分页信息###
    paginator = Paginator(branch_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/external/branch.html', locals())
