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
@login_required
@authority
def report_provide_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保明细'
    provide_typ_list = [(0, '全部'), (1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'), (41, '小贷')]  # 筛选条件
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
        tf_r = tf_r
        tl_r = tl_r
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
    TERM_LIST = [(0, '全部'), (1, '本年'), (2, '本季'), (3, '本月'), (4, '本周'), (11, '上年'), (99, '自定义'), ]

    provide_typ_list = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    provide_typ_dic = {}
    for provide_typ in provide_typ_list:
        provide_typ_dic[provide_typ[0]] = provide_typ[1]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    t_time = time.time()
    t_ctime = time.ctime()
    t_localtime = time.localtime()

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
        tf_r = tf_r
        tl_r = tl_r
    provide_groups = models.Provides.objects.filter(provide_status=1)
    if tf_r and tl_r:
        provide_groups = models.Provides.objects.filter(provide_status=1, provide_date__gte=tf_r,
                                                        provide_date__lte=tl_r)

    provide_balance = provide_groups.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 放款金额
    provide_count = provide_groups.aggregate(Count('provide_money'))['provide_money__count']  # 放款项目数

    provide_groups_breed = provide_groups.values(
        'provide_typ').annotate(
        con=Count('provide_typ'), sum=Sum('provide_balance')).values(
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
@login_required
@authority
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

    article_groups = models.Articles.objects.filter(article_balance__gt=0)

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
@login_required
@authority
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
        tf_r = tf_r
        tl_r = tl_r
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
    provide_balance = provide_list.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额

    return render(request, 'dbms/report/provide_list.html', locals())


# -----------------------放款分类统计---------------------#
@login_required
@authority
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
        tf_r = tf_r
        tl_r = tl_r
    provide_groups = models.Provides.objects.filter(provide_date__year=dt_today.year)
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
        'notify__agree__lending__summary__custom__idustry__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__custom__idustry__name', 'con', 'sum').order_by('-sum')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__district__name').annotate(
        con=Count('provide_money'), sum=Sum('provide_money')).values(
        'notify__agree__lending__summary__custom__district__name', 'con', 'sum').order_by('-sum')
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


# -----------------------项目分类统计---------------------#
@login_required
@authority
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
        tf_r = tf_r
        tl_r = tl_r
        '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    article_groups = models.Articles.objects.filter(build_date__year=dt_today.year,
                                                    article_state__in=[1, 2, 3, 4, 5, 51, 52, 55, 61])
    if tf_r and tl_r:
        article_groups = models.Articles.objects.filter(article_state__in=[1, 2, 3, 4, 5, 51, 52, 55, 61],
                                                        build_date__gte=tf_r, build_date__lte=tl_r)

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


# -----------------------客户分类统计---------------------#
@login_required
@authority
def report_custom(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户分类'
    CLASS_LIST = [(21, '区域'), (31, '行业'), (35, '部门'), (41, '项目经理'), ]
    TERM_LIST = [(11, '在保'), (21, '所有')]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    t_typ = kwargs['t_typ']
    if t_typ == 11:
        custom_groups = models.Customes.objects.filter(amount__gt=0, )
    else:
        custom_groups = models.Customes.objects.filter(custom_state=11, )
    c_credit = custom_groups.aggregate(Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    c_flow = custom_groups.aggregate(Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    c_accept = custom_groups.aggregate(Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    c_back = custom_groups.aggregate(Sum('custom_back'))['custom_back__sum']  # 保函余额
    c_entrusted = custom_groups.aggregate(Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    c_petty = custom_groups.aggregate(Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    c_amount = custom_groups.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    article_count = custom_groups.aggregate(Count('credit_amount'))['credit_amount__count']  # 客户数

    article_balance_district = custom_groups.values(
        'district__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('district__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 区域

    article_balance_idustry = custom_groups.values(
        'idustry__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('idustry__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept',
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

    return render(request, 'dbms/report/balance-class-custom.html', locals())
