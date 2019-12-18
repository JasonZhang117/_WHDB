from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, datetime, json
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


def tt_article(t_typ, tf_r, tl_r):
    dt_today = datetime.date.today()
    if t_typ == 0:
        article_groups = models.Articles.objects.filter(article_balance__gt=0)
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r, build_date__lte=tl_r)
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3, 1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3 + 2, 1) +
                                  relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r, build_date__lte=tl_r)
    elif t_typ == 3:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r, build_date__lte=tl_r)
    elif t_typ == 4:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())).isoformat()  # 本周最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r, build_date__lte=tl_r)
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r, build_date__lte=tl_r)
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r, build_date__lte=tl_r)

    return (article_groups, tf_r, tl_r)


# ----------------------报表---------------------#
@login_required
@authority
def report(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '报表系统'

    return render(request, 'dbms/report/report.html', locals())


# -----------------------在保列表---------------------#
def report_provide_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保明细'
    '''PROVIDE_TYP_LIST = [(1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'),
                        (41, '过桥贷'), (52, '房抵贷'), (53, '担保贷')]'''
    provide_typ_list = [(0, '全部'), (1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'),
                        (41, '过桥贷'), (52, '房抵贷'), (53, '担保贷')]  # 筛选条件
    TERM_LIST = [(0, '全部'), (1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    p_typ = kwargs['p_typ']

    dt_today = datetime.date.today()
    if t_typ == 0:
        pl = models.Provides.objects.filter(provide_status=1).order_by('provide_date')
        tf_r = pl.first().provide_date.isoformat()  # 本年第一天
        tl_r = pl.last().provide_date.isoformat()  # 本年最后一天
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3, 1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3 + 2, 1)
                                  + relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    provide_list = models.Provides.objects.filter(provide_status=1).select_related('notify').order_by('-provide_date')
    if tf_r and tl_r:
        if p_typ:
            provide_list = models.Provides.objects.filter(
                provide_status=1, provide_date__gte=tf_r, provide_date__lte=tl_r). \
                filter(provide_typ=p_typ).select_related('notify').order_by('-provide_date')
        else:
            provide_list = models.Provides.objects.filter(
                provide_status=1, provide_date__gte=tf_r, provide_date__lte=tl_r). \
                select_related('notify').order_by('-provide_date')

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
    provide_balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 放款金额
    provide_provide = provide_list.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额

    return render(request, 'dbms/report/provide_list.html', locals())


# -----------------------在保分类（按放款）---------------------#
def report_balance_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保分类(按放款)'
    CLASS_LIST = [(1, '品种'), (11, '授信银行'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (71, '放款支行'), (81, '法律顾问'), ]
    TERM_LIST = [(0, '全部'), (1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]
    provide_typ_list = models.Provides.PROVIDE_TYP_LIST  # 筛选条件

    provide_typ_dic = {}
    for provide_typ in provide_typ_list:
        provide_typ_dic[provide_typ[0]] = provide_typ[1]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    dt_today = datetime.date.today()
    if t_typ == 0:
        pl = models.Provides.objects.filter(provide_status=1).order_by('provide_date')
        tf_r = pl.first().provide_date.isoformat()  #
        tl_r = pl.last().provide_date.isoformat()  #
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3, 1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3 + 2, 1) +
                                  relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    provide_groups = models.Provides.objects.filter(provide_status=1)
    if tf_r and tl_r:
        provide_groups = models.Provides.objects.filter(provide_status=1, provide_date__gte=tf_r,
                                                        provide_date__lte=tl_r)

    provide_balance = provide_groups.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 放款金额
    provide_count = provide_groups.aggregate(Count('provide_money'))['provide_money__count']  # 放款项目数

    provide_groups_breed = provide_groups.values(
        'provide_typ').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'provide_typ', 'con', 'sum').order_by('-sum')
    provide_groups_director = provide_groups.values(
        'notify__agree__lending__summary__director__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__director__name', 'con', 'sum').order_by('-sum')
    provide_groups_assistant = provide_groups.values(
        'notify__agree__lending__summary__assistant__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__assistant__name', 'con', 'sum').order_by('-sum')
    provide_groups_control = provide_groups.values(
        'notify__agree__lending__summary__control__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__control__name', 'con', 'sum').order_by('-sum')
    provide_groups_idustry = provide_groups.values(
        'notify__agree__lending__summary__custom__idustry__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__custom__idustry__name', 'con', 'sum').order_by('-sum')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__district__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__custom__district__name', 'con', 'sum').order_by('-sum')
    provide_groups_bank = provide_groups.values(
        'notify__agree__branch__cooperator__short_name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__branch__cooperator__short_name', 'con', 'sum').order_by('-sum')
    provide_groups_branch = provide_groups.values(
        'notify__agree__branch__short_name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__branch__short_name', 'con', 'sum').order_by('-sum')
    provide_groups_depart = provide_groups.values(
        'notify__agree__lending__summary__director__department__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__director__department__name', 'con', 'sum').order_by('-sum')
    provide_groups_organization = provide_groups.values(
        'notify__agree__lending__summary__expert__organization').annotate(
        con=Count('provide_money'), sum=Sum('provide_balance')).values(
        'notify__agree__lending__summary__expert__organization', 'con', 'sum').order_by('-sum')

    return render(request, 'dbms/report/balance-class-provide.html', locals())


# -----------------------在保分类(按项目)---------------------#
def report_article_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保分类(按项目)'
    CLASS_LIST = [(2, '阶段'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (81, '法律顾问'), ]

    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 项目阶段
    article_state_dic = {}
    for article_state in article_state_list:
        article_state_dic[article_state[0]] = article_state[1]

    tf_r = '2019-1-1'
    tl_r = '2019-12-31'
    t_typ = 0
    article_groups, tf_r, tl_r = tt_article(t_typ, tf_r, tl_r)

    article_renewal = article_groups.aggregate(Sum('renewal'))['renewal__sum']  # 续贷金额
    article_augment = article_groups.aggregate(Sum('augment'))['augment__sum']  # 新增金额
    article_amount = article_groups.aggregate(Sum('amount'))['amount__sum']  # 金额合计
    article_notify_sum = article_groups.aggregate(Sum('article_notify_sum'))['article_notify_sum__sum']  # 通知金额
    article_provide_sum = article_groups.aggregate(Sum('article_provide_sum'))['article_provide_sum__sum']  # 放款金额
    article_repayment_sum = article_groups.aggregate(
        Sum('article_repayment_sum'))['article_repayment_sum__sum']  # 还款金额
    article_balance = article_groups.aggregate(Sum('article_balance'))['article_balance__sum']  # 在保余额
    article_count = article_groups.aggregate(Count('article_balance'))['article_balance__count']  # 项目数

    article_balance_stage = article_groups.values(
        'article_state').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('article_state', 'con', 'sum_renewal', 'sum_augment', 'sum_amount', 'sum_notify',
               'sum_provide', 'sum_repayment', 'sum_balance').order_by('article_state')  # 阶段余额分组
    article_balance_district = article_groups.values(
        'custom__district__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__district__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 区域
    article_balance_idustry = article_groups.values(
        'custom__idustry__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__idustry__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 行业
    article_balance_depart = article_groups.values(
        'director__department__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__department__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 部门
    article_balance_director = article_groups.values(
        'director__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目经理
    article_balance_assistant = article_groups.values(
        'assistant__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('assistant__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目助理
    article_balance_control = article_groups.values(
        'control__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('control__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 风控专员
    article_balance_organization = article_groups.values(
        'expert__organization').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('expert__organization', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 法律顾问

    return render(request, 'dbms/report/balance-class-article.html', locals())


# -----------------------放款列表---------------------#
def report_provide_accrual(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款明细'
    provide_typ_list = [(0, '全部'), (1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'), (41, '小贷')]  # 筛选条件
    TERM_LIST = [(1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    p_typ = kwargs['p_typ']

    dt_today = datetime.date.today()
    if t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3, 1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3 + 2, 1) +
                                  relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    provide_list = models.Provides.objects.filter(provide_date__year=dt_today.year). \
        select_related('notify').order_by('-provide_date')
    if tf_r and tl_r:
        if p_typ:
            provide_list = models.Provides.objects.filter(provide_date__gte=tf_r, provide_date__lte=tl_r). \
                filter(provide_typ=p_typ).select_related('notify').order_by('-provide_date')
        else:
            provide_list = models.Provides.objects.filter(provide_date__gte=tf_r, provide_date__lte=tl_r). \
                select_related('notify').order_by('-provide_date')

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
    provide_balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 放款金额
    provide_provide = provide_list.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额

    return render(request, 'dbms/report/provide_list.html', locals())


# -----------------------放款分类统计---------------------#
def report_accrual_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款分类'
    CLASS_LIST = [(1, '品种'), (11, '授信银行'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (71, '放款支行'), (81, '法律顾问'), ]
    TERM_LIST = [(1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    provide_typ_list = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    provide_typ_dic = {}
    for provide_typ in provide_typ_list:
        provide_typ_dic[provide_typ[0]] = provide_typ[1]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    dt_today = datetime.date.today()
    if t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3, 1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3 + 2, 1) +
                                  relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    provide_groups = models.Provides.objects.filter(provide_date__year=dt_today.year)
    if tf_r and tl_r:
        provide_groups = models.Provides.objects.filter(provide_date__gte=tf_r, provide_date__lte=tl_r)
    provide_old = provide_groups.aggregate(Sum('old_amount'))['old_amount__sum']  # 续贷金额
    provide_new = provide_groups.aggregate(Sum('new_amount'))['new_amount__sum']  # 新增金额
    provide_balance = provide_groups.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额
    provide_count = provide_groups.aggregate(Count('provide_money'))['provide_money__count']  # 放款项目数

    provide_groups_breed = provide_groups.values(
        'provide_typ').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'provide_typ', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_director = provide_groups.values(
        'notify__agree__lending__summary__director__name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__director__name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_assistant = provide_groups.values(
        'notify__agree__lending__summary__assistant__name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__assistant__name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_control = provide_groups.values(
        'notify__agree__lending__summary__control__name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__control__name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_idustry = provide_groups.values(
        'notify__agree__lending__summary__custom__idustry__name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__custom__idustry__name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__district__name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__custom__district__name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_bank = provide_groups.values(
        'notify__agree__branch__cooperator__short_name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__branch__cooperator__short_name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_branch = provide_groups.values(
        'notify__agree__branch__short_name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__branch__short_name', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')
    provide_groups_depart = provide_groups.values(
        'notify__agree__lending__summary__director__department__name').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__director__department__name', 'con', 'sum_old', 'sum_new', 'sum').order_by(
        '-sum')
    provide_groups_organization = provide_groups.values(
        'notify__agree__lending__summary__expert__organization').annotate(
        con=Count('provide_money'), sum_old=Sum('old_amount'), sum_new=Sum('new_amount'),
        sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__expert__organization', 'con', 'sum_old', 'sum_new', 'sum').order_by('-sum')

    return render(request, 'dbms/report/balance-class-accrual.html', locals())


# -----------------------项目分类统计---------------------#
def report_article(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '项目分类'
    CLASS_LIST = [(2, '阶段'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (81, '法律顾问'), ]
    TERM_LIST = [(1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 项目阶段
    article_state_dic = {}
    for article_state in article_state_list:
        article_state_dic[article_state[0]] = article_state[1]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    article_groups, tf_r, tl_r = tt_article(t_typ, tf_r, tl_r)

    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''

    article_renewal = article_groups.aggregate(Sum('renewal'))['renewal__sum']  # 续贷金额
    article_augment = article_groups.aggregate(Sum('augment'))['augment__sum']  # 新增金额
    article_amount = article_groups.aggregate(Sum('amount'))['amount__sum']  # 金额合计
    article_notify_sum = article_groups.aggregate(Sum('article_notify_sum'))['article_notify_sum__sum']  # 通知金额
    article_provide_sum = article_groups.aggregate(Sum('article_provide_sum'))['article_provide_sum__sum']  # 放款金额
    article_repayment_sum = article_groups.aggregate(
        Sum('article_repayment_sum'))['article_repayment_sum__sum']  # 还款金额
    article_balance = article_groups.aggregate(Sum('article_balance'))['article_balance__sum']  # 在保余额
    article_count = article_groups.aggregate(Count('article_balance'))['article_balance__count']  # 项目数

    article_balance_stage = article_groups.values(
        'article_state').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('article_state', 'con', 'sum_renewal', 'sum_augment', 'sum_amount', 'sum_notify',
               'sum_provide', 'sum_repayment', 'sum_balance').order_by('article_state')  # 阶段余额分组
    article_balance_district = article_groups.values(
        'custom__district__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__district__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 区域
    article_balance_idustry = article_groups.values(
        'custom__idustry__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__idustry__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 行业
    article_balance_depart = article_groups.values(
        'director__department__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__department__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 部门
    article_balance_director = article_groups.values(
        'director__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目经理
    article_balance_assistant = article_groups.values(
        'assistant__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('assistant__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目助理
    article_balance_control = article_groups.values(
        'control__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('control__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 风控专员
    article_balance_organization = article_groups.values(
        'expert__organization').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('expert__organization', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 法律顾问

    return render(request, 'dbms/report/balance-class-article.html', locals())


# -----------------------项目分类统计明细---------------------#
def report_article_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '项目分类'
    CLASS_LIST = [(2, '阶段'), (21, '区域'), (31, '行业'), (35, '部门'),
                  (41, '项目经理'), (51, '项目助理'), (61, '风控专员'), (81, '法律顾问'), ]
    TERM_LIST = [(1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 项目阶段
    article_state_dic = {}
    for article_state in article_state_list:
        article_state_dic[article_state[0]] = article_state[1]
    article_state_wen = {}
    for article_state in article_state_list:
        article_state_wen[article_state[1]] = article_state[0]
    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)

    t_typ_dic[0] = '在保'

    ss_value = request.GET.get('_cs')
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_dic_this = c_typ_dic[c_typ]
    t_typ_dic_this = t_typ_dic[t_typ]
    article_groups, tf_r, tl_r = tt_article(t_typ, tf_r, tl_r)
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''

    if c_typ == 2:
        article_groups = article_groups.filter(article_state=article_state_wen[ss_value])
    elif c_typ == 21:
        article_groups = article_groups.filter(custom__district__name=ss_value)
    elif c_typ == 31:
        article_groups = article_groups.filter(custom__idustry__name=ss_value)
    elif c_typ == 35:
        article_groups = article_groups.filter(director__department__name=ss_value)
    elif c_typ == 41:
        article_groups = article_groups.filter(director__name=ss_value)
    elif c_typ == 51:
        article_groups = article_groups.filter(assistant__name=ss_value)
    elif c_typ == 61:
        article_groups = article_groups.filter(control__name=ss_value)
    elif c_typ == 81:
        article_groups = article_groups.filter(expert__organization=ss_value)
    article_amount_tot = article_groups.aggregate(Sum('amount'))['amount__sum']  #
    article_provide_tot = article_groups.aggregate(Sum('article_provide_sum'))['article_provide_sum__sum']  #
    article_repayment_tot = article_groups.aggregate(Sum('article_repayment_sum'))['article_repayment_sum__sum']  #
    article_balance_tot = article_groups.aggregate(Sum('article_balance'))['article_balance__sum']  #
    article_acount = article_groups.count()

    return render(request, 'dbms/report/list/class-article-list.html', locals())


# -----------------------客户分类统计---------------------#
def report_custom(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户分类'
    CLASS_LIST = [(21, '区域'), (31, '行业'), (35, '部门'), (41, '管户经理'), (45, '风控专员'), ]
    TERM_LIST = [(11, '在保'), (21, '授信'), ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    industry_list = models.Industries.objects.all()
    lndustry_dic = {}
    for industry in industry_list:
        lndustry_dic[industry.code] = industry.name

    t_typ_dic = dict(TERM_LIST)
    t_typ = kwargs['t_typ']
    t_typ_t = t_typ_dic[t_typ]

    if t_typ == 11:  # 在保
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(amount__gt=0)
    else:
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(Q(credit_amount__gt=0) or Q(amount__gt=0))

    c_credit = custom_groups.aggregate(Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    c_flow = custom_groups.aggregate(Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    c_accept = custom_groups.aggregate(Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    c_back = custom_groups.aggregate(Sum('custom_back'))['custom_back__sum']  # 保函余额
    c_entrusted = custom_groups.aggregate(Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    c_petty = custom_groups.aggregate(Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    c_amount = custom_groups.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    article_count = custom_groups.aggregate(Count('credit_amount'))['credit_amount__count']  # 客户数
    c_credit_w = round(c_credit / 10000, 2)
    c_flow_w = round(c_credit / 10000, 2)
    c_accept_w = round(c_credit / 10000, 2)
    c_back_w = round(c_back / 10000, 2)
    c_entrusted_w = round(c_credit / 10000, 2)
    c_petty_w = round(c_credit / 10000, 2)
    c_amount_w = round(c_credit / 10000, 2)
    if article_count > 0:
        s_credit = round(c_credit_w / article_count, 2)
        s_flow = round(c_flow_w / article_count, 2)
        s_accept = round(c_accept_w / article_count, 2)
        s_back = round(c_back_w / article_count, 2)
        s_entrusted = round(c_entrusted / article_count, 2)
        s_petty = round(c_petty_w / article_count, 2)
        s_amount = round(c_amount_w / article_count, 2)

    article_balance_district = custom_groups.values(
        'district__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('district__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 区域

    article_balance_idustry = custom_groups.values(
        'idustry__cod_nam').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('idustry__cod_nam', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 行业
    article_balance_depart = custom_groups.values(
        'managementor__department__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('managementor__department__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 部门
    article_balance_director = custom_groups.values(
        'managementor__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('managementor__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 管户经理

    article_balance_control = custom_groups.values(
        'controler__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('controler__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 管户经理

    return render(request, 'dbms/report/balance-class-custom.html', locals())


# -----------------------客户分类统计明细---------------------#
def report_custom_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户分类'
    CLASS_LIST = [(21, '区域'), (31, '行业'), (35, '部门'), (41, '管户经理'), (45, '风控专员'), ]
    TERM_LIST = [(11, '在保'), (21, '授信'), ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    industry_list = models.Industries.objects.all()
    lndustry_dic = {}
    for industry in industry_list:
        lndustry_dic[industry.code] = industry.name
    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)
    ss_value = request.GET.get('_cs')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_this = c_typ_dic[c_typ]
    t_typ_this = t_typ_dic[t_typ]

    if t_typ == 11:  # 在保
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(amount__gt=0)
    else:
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(Q(credit_amount__gt=0) or Q(amount__gt=0))

    if c_typ == 21:
        custom_groups = custom_groups.filter(district__name=ss_value)
    elif c_typ == 31:
        custom_groups = custom_groups.filter(idustry__cod_nam=ss_value)
    elif c_typ == 35:
        custom_groups = custom_groups.filter(managementor__department__name=ss_value)
    elif c_typ == 41:
        custom_groups = custom_groups.filter(managementor__name=ss_value)
    else:
        custom_groups = custom_groups.filter(controler__name=ss_value)
    custom_credit_tot = custom_groups.aggregate(Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    custom_acount_tot = custom_groups.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    custom_acount = custom_groups.count()
    custom_credit_average = 0
    custom_acount_average = 0
    custom_credit_tot_w = custom_credit_tot / 10000
    custom_acount_tot_w = custom_acount_tot / 10000
    if custom_acount > 0:
        custom_credit_average = round(custom_credit_tot_w / custom_acount, 2)
        custom_acount_average = round(custom_acount_tot_w / custom_acount, 2)
    return render(request, 'dbms/report/list/class-custom-list.html', locals())


# -----------------------客户分类排名---------------------#
def top_custom(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户统计'
    CLASS_LIST = [(11, '在保'), (21, '授信')]
    TERM_LIST = [(7, '前五大'), (11, '前十大'), (21, '前二十大'), (99, '自定义金额')]
    CLASS_DIC = dict(CLASS_LIST)
    TERM_DIC = dict(TERM_LIST)

    industry_list = models.Industries.objects.all()
    lndustry_dic = {}
    for industry in industry_list:
        lndustry_dic[industry.code] = industry.name

    custom_groups = models.Customes.objects.exclude(custom_state=99)
    custom_groups_t = models.Customes.objects.exclude(custom_state=99)
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_c = CLASS_DIC[c_typ]
    t_typ_t = TERM_DIC[t_typ]
    screen_value = request.GET.get('ascreen')

    if c_typ == 11:  # 按在保
        custom_groups_t = custom_groups.filter(amount__gt=0)
        if t_typ == 7:  # (7, '前五大')
            custom_groups = custom_groups_t.order_by('-amount')[:5]  # 在保前五名在保余额
            screen_value = custom_groups[4].amount
        elif t_typ == 11:  # (11, '前十大')
            custom_groups = custom_groups_t.order_by('-amount')[:10]  # 在保前十名在保余额
            screen_value = custom_groups[9].amount
        elif t_typ == 21:  # (21, '前二十大')
            custom_groups = custom_groups_t.order_by('-amount')[:20]  # 在保前二十名在保余额
            screen_value = custom_groups[19].amount
        else:  # (99, '自定义金额')
            if screen_value:
                custom_groups = custom_groups_t.filter(amount__gte=screen_value).order_by('-amount')  # 按金额筛选
            else:
                screen_value = custom_groups_t.order_by('-amount')[:5][4].amount
                custom_groups = custom_groups_t.filter(amount__gte=screen_value).order_by('-amount')  # 按金额筛选
    elif c_typ == 21:  # 按授信
        custom_groups_t = custom_groups.filter(Q(credit_amount__gt=0) or Q(amount__gt=0))
        if t_typ == 7:  # (7, '前五大')
            custom_groups = custom_groups_t.order_by('-credit_amount')[:5]  # 在保前十名在保余额
            screen_value = custom_groups[4].credit_amount
        elif t_typ == 11:  # (11, '前十大')
            custom_groups = custom_groups_t.order_by('-credit_amount')[:10]  # 在保前十名在保余额
            screen_value = custom_groups[9].credit_amount
        elif t_typ == 21:  # (21, '前二十大')
            custom_groups = custom_groups_t.order_by('-credit_amount')[:20]  # 在保前二十名在保余额
            screen_value = custom_groups[19].credit_amount
        else:  # (99, '自定义金额')
            if screen_value:
                custom_groups = custom_groups_t.filter(credit_amount__gte=screen_value).order_by(
                    '-credit_amount')  # 按金额筛选
            else:
                screen_value = custom_groups_t.order_by('-amount')[:5][4].amount
                custom_groups = custom_groups_t.filter(credit_amount__gte=screen_value).order_by(
                    '-credit_amount')  # 按金额筛选
    c_credit = custom_groups.aggregate(Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    c_flow = custom_groups.aggregate(Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    c_accept = custom_groups.aggregate(Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    c_back = custom_groups.aggregate(Sum('custom_back'))['custom_back__sum']  # 保函余额
    c_entrusted = custom_groups.aggregate(Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    c_petty = custom_groups.aggregate(Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    c_amount = custom_groups.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    c_custom_count = custom_groups.aggregate(Count('credit_amount'))['credit_amount__count']  # 客户数

    t_credit = custom_groups_t.aggregate(Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    t_flow = custom_groups_t.aggregate(Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    t_accept = custom_groups_t.aggregate(Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    t_back = custom_groups_t.aggregate(Sum('custom_back'))['custom_back__sum']  # 保函余额
    t_entrusted = custom_groups_t.aggregate(Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    t_petty = custom_groups_t.aggregate(Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    t_amount = custom_groups_t.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    t_custom_count = custom_groups_t.aggregate(Count('credit_amount'))['credit_amount__count']  # 客户总数

    if t_credit > 0:
        r_credit = round(c_credit / t_credit * 100, 2)
    if t_flow > 0:
        r_flow = round(c_flow / t_flow * 100, 2)
    if t_accept > 0:
        r_accept = round(c_accept / t_accept * 100, 2)
    if t_back > 0:
        r_back = round(c_back / t_back * 100, 2)
    if t_entrusted > 0:
        r_entrusted = round(c_entrusted / t_entrusted * 100, 2)
    if t_petty > 0:
        r_petty = round(c_petty / t_petty * 100, 2)
    if t_amount > 0:
        r_amount = round(c_amount / t_amount * 100, 2)
    if t_custom_count > 0:
        r_custom_count = round(c_custom_count / t_custom_count * 100, 2)

    return render(request, 'dbms/report/top-class-custom.html', locals())


# -----------------------追偿分类统计---------------------#
def report_dun(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '追偿统计'
    TERM_LIST = [(0, '全部'), (1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    dt_today = datetime.date.today()
    if t_typ == 0:
        pl = models.Compensatories.objects.all().order_by('compensatory_date')
        tf_r = pl.first().compensatory_date.isoformat()  #
        tl_r = pl.last().compensatory_date.isoformat()  #
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3, 1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (datetime.date(dt_today.year, dt_today.month - (dt_today.month - 1) % 3 + 2, 1) +
                                  relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (dt_today - datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
        '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''

    compensatory_groups = models.Compensatories.objects.all()  # 代偿项目
    charge_groups = models.Charge.objects.all()  # 追偿费用
    retrieve_groups = models.Retrieve.objects.all()  # 案款回收

    if tf_r and tl_r:
        compensatory_groups = models.Compensatories.objects.filter(compensatory_date__gte=tf_r,
                                                                   compensatory_date__lte=tl_r)  # 代偿项目
        charge_groups = models.Charge.objects.filter(charge_date__gte=tf_r, charge_date__lte=tl_r)  # 追偿费用
        retrieve_groups = models.Retrieve.objects.filter(retrieve_date__gte=tf_r, retrieve_date__lte=tl_r)  # 案款回收

    compensatory_amount = compensatory_groups.aggregate(Sum('compensatory_amount'))['compensatory_amount__sum']  # 代偿合计
    charge_amount = charge_groups.aggregate(Sum('charge_amount'))['charge_amount__sum']  # 追偿费用合计
    retrieve_amount = retrieve_groups.aggregate(Sum('retrieve_amount'))['retrieve_amount__sum']  # 案款回收合计

    compensatory_count = compensatory_groups.aggregate(Count('compensatory_amount'))[
        'compensatory_amount__count']  # 项目数
    charge_count = charge_groups.aggregate(Count('charge_amount'))['charge_amount__count']  # 项目数
    retrieve_count = retrieve_groups.aggregate(Count('retrieve_amount'))['retrieve_amount__count']  # 项目数

    # charge_dun = charge_groups.values(
    #     'dun__compensatory__provide__notify__agree__lending__summary__custom__name').annotate(
    #     con=Count('charge_amount'), sum=Sum('charge_amount'), ). \
    #     values('dun__compensatory__provide__notify__agree__lending__summary__custom__name',
    #            'con', 'sum', ).order_by('-charge_amount')  # 追偿费用
    # retrieve_dun = retrieve_groups.values(
    #     'dun__compensatory__provide__notify__agree__lending__summary__custom__name').annotate(
    #     con=Count('retrieve_amount'), sum=Sum('retrieve_amount'), ). \
    #     values('dun__compensatory__provide__notify__agree__lending__summary__custom__name',
    #            'con', 'sum', ).order_by('-retrieve_amount')  # 案款回收

    return render(request, 'dbms/report/balance-class-dun.html', locals())


# -----------------------追偿分类统计明细---------------------#
def report_dun_dc_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户分类'
    CLASS_LIST = [(21, '区域'), (31, '行业'), (35, '部门'), (41, '管户经理'), (45, '风控专员'), ]
    TERM_LIST = [(0, '全部'), (1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    dun_dc_groups = models.Compensatories.objects.all().order_by('-compensatory_date').select_related('provide')

    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')

    t_typ = kwargs['t_typ']
    t_typ_this = t_typ_dic[t_typ]
    dun_dc_groups = models.Compensatories.objects.filter(
        compensatory_date__gte=tf_r, compensatory_date__lte=tl_r).order_by(
        '-compensatory_date').select_related('provide')
    dun_dc_capital_tot = dun_dc_groups.aggregate(Sum('compensatory_capital'))['compensatory_capital__sum']  #
    dun_dc_interest_tot = dun_dc_groups.aggregate(Sum('compensatory_interest'))['compensatory_interest__sum']  #
    dun_dc_default_tot = dun_dc_groups.aggregate(Sum('default_interest'))['default_interest__sum']  #
    dun_dc_amount_tot = dun_dc_groups.aggregate(Sum('compensatory_amount'))['compensatory_amount__sum']  #
    dun_dc_count = dun_dc_groups.count()

    return render(request, 'dbms/report/list/dun-dc-list.html', locals())
