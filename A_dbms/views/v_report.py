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
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '报表系统'

    return render(request, 'dbms/report/report.html', locals())


# -----------------------在保列表---------------------#
@login_required
@authority
def report_provide_list(request, *args, **kwargs):  #
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


# -----------------------在保分类（按放款）---------------------#
@login_required
@authority
def report_balance_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保分类(按放款)'
    CLASS_LIST = [(1, '品种'), (11, '授信银行'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (71, '放款支行'), (81, '法律顾问'), ]
    provide_typ_list = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    provide_typ_dic = {}
    for provide_typ in provide_typ_list:
        provide_typ_dic[provide_typ[0]] = provide_typ[1]
    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
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
    provide_groups_depart = provide_groups.values(
        'notify__agree__lending__summary__director__department__name').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__director__department__name', 'con', 'sum').order_by('-sum')
    provide_groups_organization = provide_groups.values(
        'notify__agree__lending__summary__expert__organization').annotate(
        con=Count('provide_balance'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__expert__organization', 'con', 'sum').order_by('-sum')

    return render(request, 'dbms/report/balance-class-provide.html', locals())


# -----------------------在保分类（按项目）---------------------#
@login_required
@authority
def report_article_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保分类(按项目)'
    CLASS_LIST = [(21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (81, '法律顾问'), ]

    article_groups = models.Articles.objects.filter(article_balance__gt=0)
    provide_balance = article_groups.aggregate(Sum('article_balance'))['article_balance__sum']  # 在保余额
    provide_count = article_groups.aggregate(Count('article_provide_sum'))['article_provide_sum__count']  # 在保项目数

    article_groups_director = article_groups.values(
        'director__name').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'director__name', 'con', 'sum').order_by('-sum')
    article_groups_assistant = article_groups.values(
        'assistant__name').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'assistant__name', 'con', 'sum').order_by('-sum')
    article_groups_control = article_groups.values(
        'control__name').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'control__name', 'con', 'sum').order_by('-sum')
    article_groups_idustry = article_groups.values(
        'custom__company_custome__idustry__name').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'custom__company_custome__idustry__name', 'con', 'sum').order_by('-sum')
    article_groups_district = article_groups.values(
        'custom__company_custome__district__name').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'custom__company_custome__district__name', 'con', 'sum').order_by('-sum')
    article_groups_depart = article_groups.values(
        'director__department__name').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'director__department__name', 'con', 'sum').order_by('-sum')
    article_groups_organization = article_groups.values(
        'expert__organization').annotate(
        con=Count('article_balance'), sum=Sum('article_balance')).values(
        'expert__organization', 'con', 'sum').order_by('-sum')
    return render(request, 'dbms/report/balance-class-article.html', locals())


# -----------------------发生额分类（按放款）---------------------#
@login_required
@authority
def report_accrual_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '发放分类(按放款)'
    CLASS_LIST = [(1, '品种'), (11, '授信银行'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (71, '放款支行'), (81, '法律顾问'), ]
    TERM_LIST = [(1, '本年度'), (11, '上年度'), (21, '前年度'), ]
    provide_typ_list = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    provide_typ_dic = {}
    for provide_typ in provide_typ_list:
        provide_typ_dic[provide_typ[0]] = provide_typ[1]

    provide_groups = models.Provides.objects.all()

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    if tf_r and tl_r:
        provide_groups = models.Provides.objects.filter(provide_date__gte=tf_r, provide_date__lte=tl_r)

    provide_balance = provide_groups.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额
    provide_count = provide_groups.aggregate(Count('provide_money'))['provide_money__count']  # 放款项目数

    provide_groups_breed = provide_groups.values(
        'provide_typ').annotate(
        con=Count('provide_typ'), sum=Sum('provide_money')).values(
        'provide_typ', 'con', 'sum').order_by('-sum')
    provide_groups_director = provide_groups.values(
        'notify__agree__lending__summary__director__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__director__name', 'con', 'sum').order_by('-sum')
    provide_groups_assistant = provide_groups.values(
        'notify__agree__lending__summary__assistant__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__assistant__name', 'con', 'sum').order_by('-sum')
    provide_groups_control = provide_groups.values(
        'notify__agree__lending__summary__control__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__control__name', 'con', 'sum').order_by('-sum')
    provide_groups_idustry = provide_groups.values(
        'notify__agree__lending__summary__custom__company_custome__idustry__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__custom__company_custome__idustry__name', 'con', 'sum').order_by('-sum')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__company_custome__district__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__custom__company_custome__district__name', 'con', 'sum').order_by('-sum')
    provide_groups_bank = provide_groups.values(
        'notify__agree__branch__cooperator__short_name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__branch__cooperator__short_name', 'con', 'sum').order_by('-sum')
    provide_groups_branch = provide_groups.values(
        'notify__agree__branch__short_name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__branch__short_name', 'con', 'sum').order_by('-sum')
    provide_groups_depart = provide_groups.values(
        'notify__agree__lending__summary__director__department__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__director__department__name', 'con', 'sum').order_by('-sum')
    provide_groups_organization = provide_groups.values(
        'notify__agree__lending__summary__expert__organization').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__expert__organization', 'con', 'sum').order_by('-sum')

    return render(request, 'dbms/report/balance-class-provide.html', locals())
