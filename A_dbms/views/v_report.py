from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, datetime, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------在保列表---------------------#
@login_required
@authority
def report(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '报表系统'

    return render(request, 'dbms/report/report.html', locals())


# -----------------------在保列表---------------------#
@login_required
@authority
def report_provide_list(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保明细'
    PROVIDE_TYP_LIST = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(provide_status=1).filter(
        **kwargs).select_related('notify').order_by('-provide_date')

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
            q.children.append(("%s__contains" % field, search_key))
        provide_list = provide_list.filter(q)
    provide_balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    return render(request, 'dbms/report/provide_list.html', locals())


# -----------------------在保列表---------------------#
@login_required
@authority
def report_balance_class(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保分类'
    print('kwargs:', kwargs,kwargs['class_typ'],type(kwargs['class_typ']))
    CLASS_LIST = [(1, '按品种'), (11, '按银行'), (21, '按区域'), (31, '按行业'), (41, '按项目经理'),
                  (51, '按项目助理'), (61, '按风控专员'), (71, '按支行'), ]
    provide_typ_list = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    provide_typ_dic = {}
    for provide_typ in provide_typ_list:
        provide_typ_dic[provide_typ[0]] = provide_typ[1]
    provide_groups = models.Provides.objects.filter(provide_status=1)
    provide_balance = provide_groups.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额
    provide_count = provide_groups.aggregate(Count('provide_money'))['provide_money__count']  # 在保项目数
    provide_groups_breed = provide_groups.values(
        'provide_typ').annotate(
        con=Count('provide_typ'), sum=Sum('provide_balance')).values(
        'provide_typ', 'con', 'sum').order_by('-sum')
    provide_groups_director = provide_groups.values(
        'notify__agree__lending__summary__director__name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__director__name', 'con', 'sum').order_by('-sum')
    provide_groups_assistant = provide_groups.values(
        'notify__agree__lending__summary__assistant__name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__assistant__name', 'con', 'sum').order_by('-sum')
    provide_groups_control = provide_groups.values(
        'notify__agree__lending__summary__control__name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__control__name', 'con', 'sum').order_by('-sum')
    provide_groups_idustry = provide_groups.values(
        'notify__agree__lending__summary__custom__company_custome__idustry__name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__custom__company_custome__idustry__name', 'con', 'sum').order_by('-sum')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__company_custome__district__name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__custom__company_custome__district__name', 'con', 'sum').order_by('-sum')
    provide_groups_bank = provide_groups.values(
        'notify__agree__branch__cooperator__short_name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__branch__cooperator__short_name', 'con', 'sum').order_by('-sum')
    provide_groups_branch = provide_groups.values(
        'notify__agree__branch__short_name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__branch__short_name', 'con', 'sum').order_by('-sum')

    return render(request, 'dbms/report/balance_class.html', locals())
